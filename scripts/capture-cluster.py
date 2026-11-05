#!/usr/bin/env python3
"""Preserve cluster inventory and pod logs locally without reading Secrets."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
K=['kubectl','--kubeconfig',str(ROOT/'.secrets/kubeconfig.yaml'),'--request-timeout=20s']
out=ROOT/'logs/kubernetes'
out.mkdir(parents=True,exist_ok=True)
while True:
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    inventory=out/'inventory'/stamp
    inventory.mkdir(parents=True,exist_ok=True)
    for resource,args in [('nodes',['get','nodes','-o','json']),('pods',['get','pods','-A','-o','json']),('storage',['get','pv,pvc,storageclasses','-A','-o','json']),('crds',['get','crds','-o','json'])]:
        try:
            q=subprocess.run(K+args,capture_output=True,text=True,timeout=25)
            (inventory/(resource+'.json')).write_text(q.stdout)
            if q.stderr:(inventory/(resource+'.stderr.txt')).write_text(q.stderr)
            if resource=='pods' and q.returncode==0:pods=json.loads(q.stdout)['items']
        except Exception as e:(inventory/(resource+'.error.txt')).write_text(str(e))
    for pod in locals().get('pods',[]):
        ns,name=pod['metadata']['namespace'],pod['metadata']['name']
        if ns not in ['glm53-research','kube-system']:continue
        folder=out/ns
        folder.mkdir(exist_ok=True)
        for previous in [False,True]:
            if previous and not any(c.get('restartCount',0) for c in pod.get('status',{}).get('containerStatuses',[])):continue
            args=['logs','-n',ns,name,'--all-containers=true','--timestamps=true']+(['--previous'] if previous else [])
            try:
                q=subprocess.run(K+args,capture_output=True,text=True,timeout=25)
                if q.returncode==0:(folder/(name+('.previous' if previous else '')+'.log')).write_text(q.stdout)
                elif q.stderr:(folder/(name+'.log-status.txt')).write_text(q.stderr)
            except subprocess.TimeoutExpired:pass
    print('Cluster capture',stamp,flush=True)
    time.sleep(20)
