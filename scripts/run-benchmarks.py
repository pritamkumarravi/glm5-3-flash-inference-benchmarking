#!/usr/bin/env python3
"""Run the real-workload matrix; preserve commands, request details and failures."""
import argparse
import datetime as dt
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base-url',required=True)
p.add_argument('--tokenizer',default='/cache/checkpoint')
p.add_argument('--profile',required=True)
p.add_argument('--suite',choices=['A','B','C','D'],required=True)
p.add_argument('--concurrency',type=int,nargs='+')
p.add_argument('--requests',type=int,default=100)
p.add_argument('--repetitions',type=int,default=3)
p.add_argument('--max-input',type=int,default=131072)
p.add_argument('--cache-control-urls',default='')
p.add_argument('--output-dir',default='/benchmarks/raw')
p.add_argument('--timeout',type=int,default=2400)
p.add_argument('--dynamo',action='store_true')
p.add_argument('--allocated-gpus',type=int,default=8)
p.add_argument('--cache-input-len',type=int,default=4096)
p.add_argument('--cache-output-len',type=int,default=1024)
p.add_argument('--prefix-groups',type=int,default=4)
p.add_argument('--prefix-fractions',type=float,nargs='+',default=[0.0,0.25,0.5,0.75])
a=p.parse_args()
script_bytes=Path(__file__).read_bytes()
loaded_script_sha256=hashlib.sha256(script_bytes).hexdigest()
assert a.requests>0 and a.repetitions>0
assert md.version('sglang')=='0.5.20','Client version changed; record and validate a new client pin'
matrix=[]
if a.suite=='A':
    matrix=[(4096,1024,c,0.0) for c in (a.concurrency or [1,4,8,16,32])]
elif a.suite=='B':
    matrix=[(n,1024,c,0.0) for n in [8192,16384,32768,65536,131072] if n<=a.max_input for c in (a.concurrency or [1])]
elif a.suite=='C':
    matrix=[(i,o,c,0.0) for i,o in [(1024,2048),(4096,4096),(8192,4096)] for c in (a.concurrency or [8,16,32,64])]
else:
    matrix=[(a.cache_input_len,a.cache_output_len,c,f) for c in (a.concurrency or [8,32]) for f in a.prefix_fractions]
root=Path(a.output_dir)/a.profile
root.mkdir(parents=True,exist_ok=True)
failures=0
for rep in range(a.repetitions):
    for isl,osl,c,fraction in matrix:
        stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        case=f'{stamp}-{a.suite}-i{isl}-o{osl}-c{c}-prefix{fraction}-rep{rep}'
        out=root/case
        out.mkdir()
        cmd=[sys.executable,str(Path(__file__).with_name('bench-entry.py')),'--backend','sglang-oai','--base-url',a.base_url,'--model','zai-org/GLM-5.3-Flash','--tokenizer',a.tokenizer,'--num-prompts',str(a.requests),'--max-concurrency',str(c),'--request-rate','inf','--temperature','0','--seed',str(42+rep),'--flush-cache','--warmup-requests',str(min(c,8)),'--cache-report','--output-details','--disable-tqdm','--output-file',str(out/'result.jsonl')]
        cmd+=['--extra-request-body',json.dumps({'stream_options':{'include_usage':True}})]
        if fraction==0:
            cmd+=['--dataset-name','random-ids','--random-input-len',str(isl),'--random-output-len',str(osl),'--random-range-ratio','1.0']
        else:
            assert a.requests%a.prefix_groups==0,'Shared-prefix requests must be divisible by prefix group count'
            shared=int(isl*fraction)
            cmd+=['--dataset-name','generated-shared-prefix','--gsp-num-groups',str(a.prefix_groups),'--gsp-prompts-per-group',str(a.requests//a.prefix_groups),'--gsp-system-prompt-len',str(shared),'--gsp-question-len',str(isl-shared),'--gsp-output-len',str(osl),'--gsp-range-ratio','1.0']
        env=os.environ.copy()
        env['GLM53_BENCHMARK_WINDOW']=str(out/'measurement-window.json')
        if a.cache_control_urls:env['GLM53_CACHE_CONTROL_URLS']=a.cache_control_urls
        if a.dynamo:env['GLM53_DYNAMO_CONTROL']='1'
        endpoints=['/engine/server_info' if a.dynamo else '/get_server_info','/metrics']
        versions={k:md.version(k) for k in ['sglang','torch','transformers','huggingface-hub']}
        metadata=dict(timestamp=stamp,profile=a.profile,suite=a.suite,input_target=isl,output_target=osl,concurrency=c,requests=a.requests,shared_prefix_fraction=fraction,repetition=rep,seed=42+rep,command=cmd,versions=versions,model_revision='46a050bec13002ad29ee795c16e61cf4fa3c4a9c',gpus_per_worker=8,dataset='random-ids' if fraction==0 else 'generated-shared-prefix',cache_control_urls=a.cache_control_urls or a.base_url)
        metadata['script_sha256']=loaded_script_sha256
        metadata['allocated_gpus']=a.allocated_gpus
        (out/'runner-source.py').write_bytes(script_bytes)
        for phase in ['before','after']:
            if phase=='after':break
            for endpoint in endpoints:
                try:
                    with urllib.request.urlopen((a.cache_control_urls or a.base_url).split(',')[0]+endpoint,timeout=15) as r:
                        (out/(endpoint.strip('/').replace('/','_')+'-before.txt')).write_bytes(r.read())
                except Exception as e:metadata[endpoint+'-before-error']=str(e)
        for worker_index,control_url in enumerate((a.cache_control_urls or a.base_url).split(',')[1:],start=1):
            for endpoint in endpoints:
                try:
                    with urllib.request.urlopen(control_url+endpoint,timeout=15) as r:
                        (out/(f'worker{worker_index}-'+endpoint.strip('/').replace('/','_')+'-before.txt')).write_bytes(r.read())
                except Exception as e:metadata[f'worker{worker_index}{endpoint}-before-error']=str(e)
        print('BENCHMARK_START',case,flush=True)
        started=time.monotonic()
        with (out/'stdout.txt').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
            try:code=subprocess.run(cmd,stdout=stdout,stderr=stderr,env=env,timeout=a.timeout).returncode
            except subprocess.TimeoutExpired:code=124
        metadata.update(exit_code=code,elapsed_seconds=time.monotonic()-started)
        results=out/'result.jsonl'
        if results.exists():
            try:
                last=json.loads(results.read_text().splitlines()[-1])
                metadata['completed']=last.get('completed')
                metadata['output_length_gate_passed']=len(last.get('output_lens',[]))==a.requests and all(n==osl for n in last.get('output_lens',[]))
                metadata['request_gate_passed']=last.get('completed')==a.requests and metadata['output_length_gate_passed']
            except Exception as e:metadata['parse_error']=str(e)
        else:metadata['request_gate_passed']=False
        for endpoint in endpoints:
            try:
                with urllib.request.urlopen((a.cache_control_urls or a.base_url).split(',')[0]+endpoint,timeout=15) as r:
                    (out/(endpoint.strip('/').replace('/','_')+'-after.txt')).write_bytes(r.read())
            except Exception as e:metadata[endpoint+'-after-error']=str(e)
        if code or not metadata.get('request_gate_passed'):failures+=1
        for worker_index,control_url in enumerate((a.cache_control_urls or a.base_url).split(',')[1:],start=1):
            for endpoint in endpoints:
                try:
                    with urllib.request.urlopen(control_url+endpoint,timeout=15) as r:
                        (out/(f'worker{worker_index}-'+endpoint.strip('/').replace('/','_')+'-after.txt')).write_bytes(r.read())
                except Exception as e:metadata[f'worker{worker_index}{endpoint}-after-error']=str(e)
        (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
        print('BENCHMARK_END',case,'exit_code',code,'completed',metadata.get('completed'),flush=True)
sys.exit(1 if failures else 0)
