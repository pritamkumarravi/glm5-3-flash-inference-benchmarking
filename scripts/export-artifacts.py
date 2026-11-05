#!/usr/bin/env python3
"""Copy only research outputs off the rentals; exclude credentials and weights."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--watch',action='store_true')
p.add_argument('--targets',default=str(ROOT/'.secrets/export-targets.json'))
a=p.parse_args()
target_file=Path(a.targets)
if not target_file.exists():
    p.error(f'Create {target_file} from configs/export-targets.example.json; rental SSH endpoints are local configuration.')
raw=json.loads(target_file.read_text())
NODES=[(x['name'],x['host'],str(x['port']),x['known_hosts']) for x in raw['nodes']]
while True:
    for name,host,port,uid in NODES:
        ssh=f'ssh -p {port} -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/Users/pkr/.lium/known_hosts/{uid}'
        for folder in ['logs','benchmarks','configs']:
            dest=ROOT/folder/'exported'/name
            dest.mkdir(parents=True,exist_ok=True)
            cmd=['rsync','-az','--partial','--timeout=30','--chmod=u=rwX,go=','--exclude=.secrets/','--exclude=*.token','--exclude=*.key','--exclude=*.pem','-e',ssh,f'root@{host}:/root/glm53-research/{folder}/',str(dest)+'/']
            try:
                q=subprocess.run(cmd,capture_output=True,text=True,timeout=50)
                msg=dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),node=name,folder=folder,exit_code=q.returncode,error=q.stderr[-1500:])
            except subprocess.TimeoutExpired:
                msg=dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),node=name,folder=folder,exit_code=124)
            with (ROOT/'logs/artifact-export.jsonl').open('a') as f:
                import json
                f.write(json.dumps(msg)+'\n')
            print(msg,flush=True)
    if not a.watch:break
    time.sleep(30)
