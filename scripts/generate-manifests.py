#!/usr/bin/env python3
"""Generate reproducible Kubernetes resources for the isolated H100 experiment."""
import json
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NS='glm53-research'
IMAGE='docker.io/glm53/sglang:0.5.20-cu130-b27fce60'
def write(name,items):
    (ROOT/'kubernetes'/name).write_text(json.dumps(dict(apiVersion='v1',kind='List',items=items),indent=2)+'\n')
def meta(name,ns=NS):
    return dict(name=name,**({'namespace':ns} if ns else {}))
items=[dict(apiVersion='v1',kind='Namespace',metadata=meta(NS,None)),dict(apiVersion='storage.k8s.io/v1',kind='StorageClass',metadata=meta('glm53-local',None),provisioner='kubernetes.io/no-provisioner',volumeBindingMode='WaitForFirstConsumer',reclaimPolicy='Retain')]
for rank in range(2):
    items.append(dict(apiVersion='v1',kind='PersistentVolume',metadata=meta(f'glm53-model-{rank}',None),spec=dict(capacity={'storage':'600Gi'},volumeMode='Filesystem',accessModes=['ReadWriteOnce'],persistentVolumeReclaimPolicy='Retain',storageClassName='glm53-local',local={'path':'/root/glm53-research/model-cache'},nodeAffinity={'required':{'nodeSelectorTerms':[{'matchExpressions':[{'key':'kubernetes.io/hostname','operator':'In','values':[f'glm53-h100-{rank}']}]}]}})))
    items.append(dict(apiVersion='v1',kind='PersistentVolumeClaim',metadata=meta(f'model-{rank}'),spec=dict(accessModes=['ReadWriteOnce'],storageClassName='glm53-local',volumeName=f'glm53-model-{rank}',resources={'requests':{'storage':'600Gi'}})))
write('storage.json',items)
jobs=[]
for rank in range(2):
    jobs.append(dict(apiVersion='batch/v1',kind='Job',metadata=meta(f'gpu-validation-{rank}'),spec=dict(backoffLimit=0,template=dict(metadata={'labels':{'app':'gpu-validation'}},spec=dict(restartPolicy='Never',runtimeClassName='nvidia',nodeSelector={'kubernetes.io/hostname':f'glm53-h100-{rank}'},containers=[dict(name='validate',image=IMAGE,imagePullPolicy='Never',command=['python3','-c','import torch, json; assert torch.cuda.device_count()==8; print(json.dumps({"torch":torch.__version__,"cuda":torch.version.cuda,"nccl":torch.cuda.nccl.version(),"gpus":[torch.cuda.get_device_name(i) for i in range(8)]})); print([torch.ones(4,device=f"cuda:{i}").sum().item() for i in range(8)])'],resources={'limits':{'nvidia.com/gpu':8},'requests':{'cpu':2,'memory':'8Gi','nvidia.com/gpu':8}})])))))
write('gpu-validation.json',jobs)
script_data={p.name:p.read_text() for p in (ROOT/'scripts').glob('*.py') if p.name in ['download-model.py','run-benchmarks.py','verify-serving.py','bench-entry.py']}
cm_name='research-scripts-'+hashlib.sha256(json.dumps(script_data,sort_keys=True).encode()).hexdigest()[:16]
cm=dict(apiVersion='v1',kind='ConfigMap',metadata=meta(cm_name),immutable=True,data=script_data)
write('research-scripts.json',[cm])
(ROOT/'kubernetes/configmaps').mkdir(exist_ok=True)
(ROOT/'kubernetes/configmaps'/f'{cm_name}.json').write_text(json.dumps(cm,indent=2)+'\n')
jobs=[]
for rank in range(2):
    container=dict(name='download',image=IMAGE,imagePullPolicy='Never',command=['bash','-lc','set -o pipefail; python3 -u /research/download-model.py 2>&1 | tee /logs/model-download.log'],env=[{'name':'HF_HOME','value':'/cache/hf'},{'name':'HF_XET_HIGH_PERFORMANCE','value':'1'},{'name':'NVIDIA_VISIBLE_DEVICES','value':'void'}],resources={'requests':{'cpu':8,'memory':'32Gi'},'limits':{'memory':'64Gi'}},volumeMounts=[{'name':'cache','mountPath':'/cache'},{'name':'scripts','mountPath':'/research','readOnly':True},{'name':'logs','mountPath':'/logs'}])
    jobs.append(dict(apiVersion='batch/v1',kind='Job',metadata=meta(f'model-download-{rank}'),spec=dict(backoffLimit=1,template=dict(metadata={'labels':{'app':'model-download'}},spec=dict(restartPolicy='Never',nodeSelector={'kubernetes.io/hostname':f'glm53-h100-{rank}'},containers=[container],volumes=[{'name':'cache','persistentVolumeClaim':{'claimName':f'model-{rank}'}},{'name':'scripts','configMap':{'name':cm_name}},{'name':'logs','hostPath':{'path':'/root/glm53-research/logs/infrastructure','type':'DirectoryOrCreate'}}])))))
write('model-download.json',jobs)
print('Generated storage, GPU-validation, research-scripts and model-download manifests.')
