#!/usr/bin/env python3
"""Check real responses, concurrent generation, repeated prefixes, and tools."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path
import re
import time
import urllib.request

p=argparse.ArgumentParser()
p.add_argument('--base-url',required=True)
p.add_argument('--output',required=True)
p.add_argument('--concurrency',type=int,nargs='+',default=[1,8,32])
a=p.parse_args()
deadline=time.monotonic()+600
while True:
    try:
        with urllib.request.urlopen(a.base_url.rstrip('/')+'/health',timeout=5) as response:
            healthy=response.status==200
        with urllib.request.urlopen(a.base_url.rstrip('/')+'/v1/models',timeout=5) as response:
            models=json.load(response)
        if healthy and any(m.get('id')=='zai-org/GLM-5.3-Flash' for m in models.get('data',[])):break
    except Exception:
        if time.monotonic()>=deadline:raise TimeoutError('Serving endpoint did not become healthy within 600 seconds')
    time.sleep(2)
def request(body):
    req=urllib.request.Request(a.base_url.rstrip('/')+'/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
tests=[]
def arithmetic(i):
    x,y=(i*7)%43+1,(i*11)%37+1
    prompt=f'Compute {x} + {y}. Reply with only the integer sum.'
    body=dict(model='zai-org/GLM-5.3-Flash',messages=[{'role':'user','content':prompt}],max_tokens=512,temperature=0)
    try:
        response=request(body)
        text=response['choices'][0]['message'].get('content') or ''
        found=re.findall(r'\b\d+\b',text)
        passed=found==[str(x+y)]
        return dict(prompt=prompt,expected=str(x+y),response=response,passed=passed)
    except Exception as e:return dict(prompt=prompt,passed=False,error=str(e))
for concurrency in a.concurrency:
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        rows=list(pool.map(arithmetic,range(max(concurrency,8))))
    tests.append(dict(type='arithmetic',concurrency=concurrency,results=rows,passed=all(r['passed'] for r in rows)))
sentinel='The exact private project codename in this document is cobalt-orchid-7319.'
context=('This report discusses GPU scheduling, model caching, batch allocation, and network measurements. '*100)+sentinel+(' Preserve accurate observations separately from estimates. '*100)
prefix_results=[]
for attempt in range(3):
    body=dict(model='zai-org/GLM-5.3-Flash',messages=[{'role':'user','content':context+'\nWhat is the exact project codename? Reply with only the codename.'}],max_tokens=512,temperature=0)
    try:
        response=request(body)
        content=response['choices'][0]['message'].get('content') or ''
        prefix_results.append(dict(attempt=attempt,response=response,passed='cobalt-orchid-7319' in content))
    except Exception as e:prefix_results.append(dict(attempt=attempt,passed=False,error=str(e)))
tests.append(dict(type='repeated-prefix-retrieval',results=prefix_results,passed=all(r['passed'] for r in prefix_results)))
tool={'type':'function','function':{'name':'lookup_city','description':'Look up the named city.','parameters':{'type':'object','properties':{'city':{'type':'string'}},'required':['city']}}}
try:
    response=request(dict(model='zai-org/GLM-5.3-Flash',messages=[{'role':'user','content':'Use lookup_city to look up Helsinki.'}],tools=[tool],tool_choice={'type':'function','function':{'name':'lookup_city'}},temperature=0,max_tokens=512))
    calls=response['choices'][0]['message'].get('tool_calls') or []
    passed=bool(calls) and calls[0]['function']['name']=='lookup_city' and json.loads(calls[0]['function']['arguments']).get('city','').lower()=='helsinki'
    tests.append(dict(type='tool-parser',response=response,passed=passed))
except Exception as e:tests.append(dict(type='tool-parser',passed=False,error=str(e)))
result=dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),base_url=a.base_url,tests=tests,passed=all(t['passed'] for t in tests))
out=Path(a.output)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'checks':[{'type':t['type'],'passed':t['passed']} for t in tests]},indent=2))
raise SystemExit(0 if result['passed'] else 1)
