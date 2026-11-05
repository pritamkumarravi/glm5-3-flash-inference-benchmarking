#!/usr/bin/env python3
"""Use the pinned engine benchmark with explicit worker cache-control URLs."""
import os
import requests
import inspect
import json
import time
from pathlib import Path
from sglang.benchmark import serving

# The 0.5.20 completions client indexes choices[0] on usage-only SSE chunks.
# Preserve usage counts, then skip empty choices; the engine is unchanged.
source=inspect.getsource(serving.async_request_openai_completions)
anchor='if data["choices"][0]["text"]:'
assert source.count(anchor)==1,'Pinned benchmark source changed; revalidate the compatibility patch'
source=source.replace(anchor,'output_len = (data.get("usage") or {}).get("completion_tokens", output_len)\n                            if (data.get("choices") or []) and data["choices"][0]["text"]:')
exec(compile(source,'sglang-0.5.20-completions-usage-fix','exec'),serving.__dict__)
serving.ASYNC_REQUEST_FUNCS['sglang-oai']=serving.async_request_openai_completions
if os.environ.get('GLM53_DYNAMO_CONTROL')=='1':
    source=inspect.getsource(serving.run_benchmark)
    anchor='extra_request_body["return_cached_tokens_details"] = True'
    assert source.count(anchor)==1
    source=source.replace(anchor,'pass  # Dynamo rejects native cache-detail request fields; use worker metrics.')
    exec(compile(source,'sglang-0.5.20-dynamo-request-adapter','exec'),serving.__dict__)

windows=[]
def mark(stage):
    windows.append({'stage':stage,'wall_time':time.time(),'monotonic':time.perf_counter()})
def server_info(base_url):
    control=os.environ.get('GLM53_CACHE_CONTROL_URLS',base_url).split(',')[0].rstrip('/')
    path='/engine/server_info' if os.environ.get('GLM53_DYNAMO_CONTROL')=='1' else '/server_info'
    try:
        return requests.get(control+path,timeout=10)
    except requests.RequestException as exc:
        # A metadata lookup must not discard completed request measurements.
        print('SERVER_INFO_LOOKUP_FAILED',str(exc),flush=True)
        response=requests.Response()
        response.status_code=503
        response._content=b'{}'
        return response
serving.__dict__['_glm53_mark']=mark
serving.__dict__['_glm53_server_info']=server_info
source=inspect.getsource(serving.benchmark)
start_anchor='benchmark_start_time = time.perf_counter()'
end_anchor='    if "sglang" in backend:\n        server_info = requests.get(\n            base_url + "/server_info", headers=get_auth_headers()\n        )'
assert source.count(start_anchor)==1 and source.count(end_anchor)==1
source=source.replace(start_anchor,start_anchor+'\n    _glm53_mark("start")')
source=source.replace(end_anchor,'    _glm53_end = time.perf_counter()\n    _glm53_mark("end")\n    if "sglang" in backend:\n        server_info = _glm53_server_info(base_url)')
source=source.replace('benchmark_duration = time.perf_counter() - benchmark_start_time','benchmark_duration = _glm53_end - benchmark_start_time')
exec(compile(source,'sglang-0.5.20-benchmark-control-adapter','exec'),serving.__dict__)

original=serving.flush_server_cache
def flush(base_url,backend,flush_cache_timeout=60.0):
    urls=os.environ.get('GLM53_CACHE_CONTROL_URLS',base_url).split(',')
    for url in urls:
        if os.environ.get('GLM53_DYNAMO_CONTROL')=='1':
            result=requests.post(url.rstrip('/')+'/engine/flush_cache',json={},timeout=flush_cache_timeout+10)
            result.raise_for_status()
            if result.json() is False or (isinstance(result.json(),dict) and result.json().get('success') is False):
                raise RuntimeError('Dynamo worker refused cache flush: '+result.text)
        else:
            original(url.rstrip('/'),backend,flush_cache_timeout)
serving.flush_server_cache=flush
try:
    serving.cli_main()
finally:
    if os.environ.get('GLM53_BENCHMARK_WINDOW'):
        Path(os.environ['GLM53_BENCHMARK_WINDOW']).write_text(json.dumps(windows,indent=2)+'\n')
