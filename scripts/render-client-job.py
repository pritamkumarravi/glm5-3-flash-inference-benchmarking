#!/usr/bin/env python3
"""Render a CPU-only, node-local correctness or benchmark client Job."""
import argparse
import json
from pathlib import Path

r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--name',required=True)
p.add_argument('--node',required=True,type=int,choices=[0,1])
p.add_argument('--verify',action='store_true')
p.add_argument('--profile',required=True)
p.add_argument('--suite',default='A',choices=['A','B','C','D'])
p.add_argument('--concurrency',type=int,nargs='+',default=[8,16,32,4,1])
p.add_argument('--requests',type=int,default=100)
p.add_argument('--repetitions',type=int,default=1)
p.add_argument('--base-url')
p.add_argument('--dynamo',action='store_true')
p.add_argument('--allocated-gpus',type=int,default=8)
p.add_argument('--cache-control-urls')
p.add_argument('--cache-input-len',type=int,default=4096)
p.add_argument('--cache-output-len',type=int,default=1024)
p.add_argument('--prefix-groups',type=int,default=4)
p.add_argument('--prefix-fractions',type=float,nargs='+',default=[0.0,0.25,0.5,0.75])
a=p.parse_args()
url=a.base_url or f'http://aggregated-{a.node}:30000'
if a.verify:
    cmd=['python3','-u','/research/verify-serving.py','--base-url',url,'--output',f'/benchmarks/correctness/{a.profile}-{a.name}.json']
else:
    cmd=['python3','-u','/research/run-benchmarks.py','--base-url',url,'--profile',a.profile,'--suite',a.suite,'--concurrency',*[str(x) for x in a.concurrency],'--requests',str(a.requests),'--repetitions',str(a.repetitions)]
    cmd += ['--cache-input-len',str(a.cache_input_len),'--cache-output-len',str(a.cache_output_len),'--prefix-groups',str(a.prefix_groups),'--prefix-fractions',*[str(x) for x in a.prefix_fractions]]
    if a.dynamo:cmd+=['--dynamo']
    cmd+=['--allocated-gpus',str(a.allocated_gpus)]
    if a.cache_control_urls:cmd+=['--cache-control-urls',a.cache_control_urls]
cm_name=json.loads((r/'kubernetes/research-scripts.json').read_text())['items'][0]['metadata']['name']
volumes=[{'name':'cache','persistentVolumeClaim':{'claimName':f'model-{a.node}'}},{'name':'scripts','configMap':{'name':cm_name}},{'name':'results','hostPath':{'path':'/root/glm53-research/benchmarks','type':'DirectoryOrCreate'}}]
container={'name':'client','image':'docker.io/glm53/sglang:0.5.20-cu130-b27fce60','imagePullPolicy':'Never','command':cmd,'env':[{'name':'NVIDIA_VISIBLE_DEVICES','value':'void'},{'name':'HF_HOME','value':'/cache/hf'},{'name':'HF_HUB_OFFLINE','value':'1'},{'name':'TRANSFORMERS_OFFLINE','value':'1'},{'name':'OMP_NUM_THREADS','value':'4'}],'resources':{'requests':{'cpu':4,'memory':'16Gi'},'limits':{'memory':'32Gi'}},'volumeMounts':[{'name':'cache','mountPath':'/cache','readOnly':True},{'name':'scripts','mountPath':'/research','readOnly':True},{'name':'results','mountPath':'/benchmarks'}]}
# No GPU resource is requested. The client performs tokenization and HTTP I/O.
job={'apiVersion':'batch/v1','kind':'Job','metadata':{'name':a.name,'namespace':'glm53-research'},'spec':{'backoffLimit':0,'template':{'metadata':{'labels':{'app':'research-client','profile':a.profile}},'spec':{'restartPolicy':'Never','nodeSelector':{'kubernetes.io/hostname':f'glm53-h100-{a.node}'},'containers':[container],'volumes':volumes}}}}
path=r/'kubernetes'/f'{a.name}.json'
path.write_text(json.dumps(job,indent=2)+'\n')
print(path)
