#!/usr/bin/env python3
"""Gate the experimental PD allocation on two completed aggregate cache runs."""
import datetime as dt
import json
import fcntl
import sys
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
lock=(ROOT/'logs/pd-transition.lock').open('w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
K=['kubectl','--request-timeout=45s','--kubeconfig',str(ROOT/'.secrets/kubeconfig.yaml'),'-n','glm53-research']
jobs=['cache-pressure-dynamo-host32','cache-pressure-dynamo-host64']
while True:
    p=subprocess.run(K+['get','jobs',*jobs,'-o','json'],capture_output=True,text=True,timeout=30)
    if p.returncode: raise SystemExit(p.stderr)
    items=json.loads(p.stdout)['items']
    if any(x.get('status',{}).get('failed',0) for x in items): raise SystemExit('Cache run failed: preserve aggregated workers for diagnosis')
    if all(x.get('status',{}).get('succeeded',0)==1 for x in items):break
    if dt.datetime.now(dt.timezone.utc).hour>=11:raise SystemExit('Deadline expired')
    time.sleep(15)
subprocess.run(K+['apply','-f',str(ROOT/'kubernetes/verify-dynamo-host64-post.json')],check=True)
subprocess.run(K+['wait','--for=condition=complete','job/verify-dynamo-host64-post','--timeout=180s'],check=True)
commands=[K+['scale','deployment','aggregated-0','aggregated-1','--replicas=0'],K+['apply','-f',str(ROOT/'kubernetes/pd-nixl.json')],K+['apply','-f',str(ROOT/'kubernetes/verify-pd-nixl.json')]]
for index,cmd in enumerate(commands):
    subprocess.run([sys.executable,str(ROOT/'scripts/record.py'),'--label',f'pd-nixl-transition-{index}','--node','both','--configuration','TP8 per role, EP1, CP1, NIXL, no speculation or host cache','--runtime-version','SGLang 0.5.20; Dynamo 1.6.0; NIXL 1.5.0','--model-revision','46a050bec13002ad29ee795c16e61cf4fa3c4a9c','--interpretation','Cache benchmarks completed. Starting PD validation; performance and transport remain unverified.','--',*cmd],cwd=ROOT,check=True)
