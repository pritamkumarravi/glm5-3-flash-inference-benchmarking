#!/usr/bin/env python3
"""Render one explicitly named H100 experiment; no runtime/version substitutions."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--profile',required=True,choices=['fpm-ep1-l1','cookbook-ep8-l1','fpm-ep1-cacheoff','fpm-ep1-host32','fpm-ep1-host64','fpm-ep1-host64-selective','fpm-ep1-mtp516'])
p.add_argument('--node',required=True,type=int,choices=[0,1])
p.add_argument('--mem-fraction',type=float,default=0.70)
p.add_argument('--max-running',type=int,default=32)
p.add_argument('--mamba-ratio',type=float,default=0.9)
p.add_argument('--mamba-cache-size',type=int)
p.add_argument('--max-total-tokens',type=int)
p.add_argument('--chunk-size',type=int,default=8192)
p.add_argument('--image',default='docker.io/glm53/sglang:0.5.20-cu130-b27fce60')
p.add_argument('--dynamo',action='store_true')
p.add_argument('--namespace',default='glm53')
a=p.parse_args()
assert 0<a.mem_fraction<1 and a.max_running>0 and a.mamba_ratio>0
args=['--model-path','/cache/checkpoint','--served-model-name','zai-org/GLM-5.3-Flash','--tp-size','8','--ep-size','8' if a.profile=='cookbook-ep8-l1' else '1','--quantization','fp8','--kv-cache-dtype','bfloat16','--dsa-prefill-backend','tilelang','--dsa-decode-backend','tilelang','--moe-runner-backend','deep_gemm','--reasoning-parser','auto','--tool-call-parser','auto','--context-length','1048576','--mem-fraction-static',str(a.mem_fraction),'--max-running-requests',str(a.max_running),'--chunked-prefill-size',str(a.chunk_size),'--max-prefill-tokens',str(a.chunk_size),'--mamba-full-memory-ratio',str(a.mamba_ratio),'--enable-metrics','--watchdog-timeout','1200','--host','0.0.0.0','--port','30000']
if a.mamba_cache_size:args+=['--max-mamba-cache-size',str(a.mamba_cache_size)]
if a.max_total_tokens:args+=['--max-total-tokens',str(a.max_total_tokens)]
if a.profile=='fpm-ep1-cacheoff':args+=['--disable-radix-cache']
if 'host' in a.profile:
    size='32' if 'host32' in a.profile else '64'
    args+=['--enable-hierarchical-cache','--hicache-size',size,'--hicache-write-policy','write_through_selective' if 'selective' in a.profile else 'write_through']
if a.profile=='fpm-ep1-mtp516':args+=['--speculative-algorithm','EAGLE','--speculative-num-steps','5','--speculative-eagle-topk','1','--speculative-num-draft-tokens','6']
launch=['python3','-m','sglang.launch_server']
if a.dynamo:
    launch=['python3','-m','dynamo.sglang']
    for native,dyn,value in [('--reasoning-parser','--dyn-reasoning-parser','glm45'),('--tool-call-parser','--dyn-tool-call-parser','glm47')]:
        index=args.index(native)
        args[index:index+2]=[dyn,value]
    args+=['--engine-route','flush_cache','--engine-route','server_info=get_server_info','--kv-events-config','{"publisher":"zmq","endpoint":"tcp://*:5557","topic":"kv-events","replay_buffer_size":10000}']
name=f'aggregated-{a.node}'
env=[{'name':'HF_HOME','value':'/cache/hf'},{'name':'HF_HUB_OFFLINE','value':'1'},{'name':'TRANSFORMERS_OFFLINE','value':'1'},{'name':'OMP_NUM_THREADS','value':'8'},{'name':'NCCL_DEBUG','value':'INFO'},{'name':'DYN_NAMESPACE','value':'glm53'},{'name':'ETCD_ENDPOINTS','value':'http://etcd:2379'},{'name':'NATS_SERVER','value':'nats://nats:4222'}]
for entry in env:
    if entry['name']=='DYN_NAMESPACE':entry['value']=a.namespace
if a.dynamo:
    env=[e for e in env if e['name']!='NATS_SERVER']
    env += [{'name':'DYN_DISCOVERY_BACKEND','value':'etcd'},{'name':'DYN_EVENT_PLANE','value':'zmq'},{'name':'DYN_REQUEST_PLANE','value':'tcp'},{'name':'DYN_RESPONSE_PLANE','value':'tcp'},{'name':'DYN_SYSTEM_PORT','value':'8081'}]
import shlex
shell='set -euo pipefail; test -f /cache/download-manifest.json; '+shlex.join(launch+args)+' 2>&1 | tee -a /logs/'+a.profile+'-${HOSTNAME}.log'
volumes=[{'name':'cache','persistentVolumeClaim':{'claimName':f'model-{a.node}'}},{'name':'shm','emptyDir':{'medium':'Memory','sizeLimit':'128Gi'}},{'name':'logs','hostPath':{'path':'/root/glm53-research/logs/sglang','type':'DirectoryOrCreate'}}]
c=dict(name='worker',image=a.image,imagePullPolicy='Never',command=['bash','-lc',shell],env=env,ports=[{'containerPort':30000,'name':'http'},{'containerPort':8081,'name':'metrics'}],resources={'requests':{'cpu':32,'memory':'800Gi','nvidia.com/gpu':8},'limits':{'memory':'1100Gi','nvidia.com/gpu':8}},securityContext={'capabilities':{'add':['IPC_LOCK','SYS_RESOURCE']}},volumeMounts=[{'name':'cache','mountPath':'/cache'},{'name':'cache','mountPath':'/root/.cache','subPath':'kernel-cache/root-cache'},{'name':'cache','mountPath':'/root/.triton','subPath':'kernel-cache/triton'},{'name':'shm','mountPath':'/dev/shm'},{'name':'logs','mountPath':'/logs'}],startupProbe={'httpGet':{'path':'/health','port':'http'},'failureThreshold':180,'periodSeconds':10,'timeoutSeconds':30},readinessProbe={'httpGet':{'path':'/health','port':'http'},'periodSeconds':10,'timeoutSeconds':30})
if a.dynamo:
    c.pop('startupProbe');c.pop('readinessProbe')
labels={'app':name,'profile':a.profile}
deployment=dict(apiVersion='apps/v1',kind='Deployment',metadata={'name':name,'namespace':'glm53-research'},spec=dict(replicas=1,strategy={'type':'Recreate'},selector={'matchLabels':{'app':name}},template={'metadata':{'labels':labels,'annotations':{'research.model-revision':'46a050bec13002ad29ee795c16e61cf4fa3c4a9c','research.validation':'pending real-weight checks'}},'spec':{'runtimeClassName':'nvidia','nodeSelector':{'kubernetes.io/hostname':f'glm53-h100-{a.node}'},'terminationGracePeriodSeconds':90,'containers':[c],'volumes':volumes}}))
deployment['spec']['template']['spec']['initContainers']=[dict(name='prepare-cache',image=a.image,imagePullPolicy='Never',command=['bash','-lc','mkdir -p /cache/kernel-cache/root-cache /cache/kernel-cache/triton'],env=[{'name':'NVIDIA_VISIBLE_DEVICES','value':'void'}],volumeMounts=[{'name':'cache','mountPath':'/cache'}])]
service=dict(apiVersion='v1',kind='Service',metadata={'name':name,'namespace':'glm53-research'},spec={'selector':{'app':name},'ports':[{'name':'http','port':30000,'targetPort':'http'},{'name':'metrics','port':8081,'targetPort':'metrics'}]})
service['spec']['publishNotReadyAddresses']=True
out=ROOT/'kubernetes'/f'{name}-{a.profile}.json'
out.write_text(json.dumps({'apiVersion':'v1','kind':'List','items':[deployment,service]},indent=2)+'\n')
profile=dict(name=a.profile,node=a.node,image=a.image,model_revision='46a050bec13002ad29ee795c16e61cf4fa3c4a9c',launch=launch,args=args,validated=False,measured=False)
(ROOT/'configs/aggregated'/f'{a.profile}-node{a.node}.json').write_text(json.dumps(profile,indent=2)+'\n')
print(out)
