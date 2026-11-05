#!/usr/bin/env python3
"""Execute gated, sequential PD cache comparisons; preserve each transition."""
import argparse
import datetime as dt
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
lock=(ROOT/'logs/pd-cache-sequence.lock').open('w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
K=['kubectl','--request-timeout=20s','--kubeconfig',str(ROOT/'.secrets/kubeconfig.yaml'),'-n','glm53-research']
stop=dt.datetime(2026,11,4,10,34,tzinfo=dt.timezone.utc)
def check_deadline():
    if dt.datetime.now(dt.timezone.utc)>=stop:raise SystemExit('Stop before rental removal; leave artifacts for export')
def query(args):
    r=subprocess.run(K+args,capture_output=True,text=True,timeout=35)
    if r.returncode:raise RuntimeError(r.stderr)
    return r.stdout
def wait_job(name,timeout=600):
    deadline=time.monotonic()+timeout
    while True:
        check_deadline()
        try:
            status=json.loads(query(['get','job',name,'-o','json'])).get('status',{})
            if status.get('failed'):raise SystemExit(f'Job failed: {name}; do not advance')
            if status.get('succeeded')==1:return
        except (RuntimeError,subprocess.TimeoutExpired) as e:print(str(e),flush=True)
        if time.monotonic()>deadline:raise SystemExit(f'Job did not finish: {name}')
        time.sleep(10)
def apply(path,label):
    check_deadline()
    command=[sys.executable,str(ROOT/'scripts/record.py'),'--label',label,'--node','both','--configuration',path,'--runtime-version','SGLang0.5.20 Dynamo1.6.0 NIXL1.5.0','--model-revision','46a050bec13002ad29ee795c16e61cf4fa3c4a9c','--interpretation','Sequential PD comparison; correctness gate required before performance.','--',*K,'apply','-f',str(ROOT/path)]
    for attempt in range(3):
        if subprocess.run(command,cwd=ROOT).returncode==0:return
    raise SystemExit(f'Apply failed: {path}')
def run_job(name):
    apply(f'kubernetes/{name}.json',name)
    wait_job(name)
parser=argparse.ArgumentParser()
parser.add_argument('--resume-host64',action='store_true')
args=parser.parse_args()
if not args.resume_host64:
    wait_job('bench-pd-nixl-pressure')
    run_job('bench-pd-nixl-32k-c32')
    apply('kubernetes/pd-nixl-host64.json','pd-prefill-host64-transition')
ready_deadline=time.monotonic()+600
code="import urllib.request,json; d=json.load(urllib.request.urlopen('http://pd-nixl-prefill:8081/engine/server_info',timeout=10)); assert d.get('enable_hierarchical_cache') and d.get('hicache_size')==64; print('NEW_HOST64_PREFILL_READY')"
while True:
    check_deadline()
    try:
        r=query(['exec','deployment/dynamo-frontend-pd','--','python3','-c',code])
        if 'NEW_HOST64_PREFILL_READY' in r:break
    except (RuntimeError,subprocess.TimeoutExpired):pass
    if time.monotonic()>ready_deadline:raise SystemExit('Host64 prefill startup failed')
    time.sleep(10)
run_job('verify-pd-nixl-host64')
run_job('bench-pd-nixl-host64-pressure')
run_job('bench-pd-nixl-host64-64k-c128')
if (stop-dt.datetime.now(dt.timezone.utc)).total_seconds()>240:
    run_job('bench-pd-nixl-host64-32k-scale')
print('PD_HICACHE_SEQUENCE_COMPLETE',flush=True)
