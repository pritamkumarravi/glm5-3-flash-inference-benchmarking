#!/usr/bin/env python3
"""Read model/runtime metadata without downloading weights or installing packages."""
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'environment/sources/metadata'
OUT.mkdir(parents=True,exist_ok=True)
def fetch(url,path):
    req=urllib.request.Request(url,headers={'User-Agent':'glm53-research-readonly'})
    try:
        with urllib.request.urlopen(req,timeout=40) as r: body=r.read()
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(body)
        print('SAVED',url,len(body),hashlib.sha256(body).hexdigest(),flush=True)
        return json.loads(body) if path.suffix=='.json' else body
    except urllib.error.HTTPError as e:
        print('HTTP_ERROR',e.code,url,flush=True)
    except Exception as e:
        print('ERROR',type(e).__name__,str(e),url,flush=True)

model=fetch('https://huggingface.co/api/models/zai-org/GLM-5.3-Flash?blobs=true',OUT/'model-info.json')
if model:
    sha=model['sha']
    print('MODEL_REVISION',sha,'gated',model.get('gated'),flush=True)
    for name in ['config.json','generation_config.json','model.safetensors.index.json']:
        fetch(f'https://huggingface.co/zai-org/GLM-5.3-Flash/resolve/{sha}/{name}',OUT/name)
    files=[x for x in model.get('siblings',[]) if x['rfilename'].endswith('.safetensors')]
    print('MODEL_SHARDS',len(files),'TOTAL_BYTES',sum(x.get('size',0) for x in files),flush=True)
for package,version in [('sglang','0.5.20'),('ai-dynamo','1.6.0'),('aiperf','0.10.0')]:
    data=fetch(f'https://pypi.org/pypi/{package}/{version}/json',OUT/f'{package}-{version}.json')
    if data: print('REQUIRES',package,data['info'].get('requires_python'),data['info'].get('requires_dist'),flush=True)
for repo in ['sgl-project/sglang','ai-dynamo/dynamo']:
    folder=next((ROOT/'environment/sources'/repo.replace('/','--')).iterdir())
    tree=json.loads((folder/'tree.json').read_text())['tree']
    available={x['path'] for x in tree if x['type']=='blob'}
    if repo=='sgl-project/sglang':
        wanted=[p for p in available if p in ['python/pyproject.toml','python/sglang/srt/mem_cache/hiradix_cache.py','python/sglang/srt/mem_cache/hybrid_radix_cache.py','python/sglang/srt/mem_cache/memory_pool_host.py','python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py','python/sglang/benchmark/serving.py']]
        wanted += [p for p in available if p.startswith('python/sglang/srt/disaggregation/') and p.endswith('.py') and ('common' in p or 'mooncake' in p)]
    else:
        wanted=[p for p in available if p.startswith(('components/src/dynamo/sglang/','examples/backends/sglang/','docs/fern/pages/backends/sglang/','docs/fern/pages/kubernetes/getting-started/')) and p.endswith(('.py','.sh','.md','.mdx','.yaml'))]
    for path in sorted(set(wanted)):
        fetch(f'https://raw.githubusercontent.com/{repo}/{folder.name}/{path}',folder/path)
tag=fetch('https://api.github.com/repos/sgl-project/sglang/git/ref/tags/v0.5.20',OUT/'sglang-v0.5.20-tag.json')
if tag:
    ref=tag['object']['sha']
    if tag['object']['type']=='tag':
        annotated=fetch(f'https://api.github.com/repos/sgl-project/sglang/git/tags/{ref}',OUT/'sglang-v0.5.20-annotated.json')
        ref=annotated['object']['sha']
    for path in ['python/sglang/srt/server_args.py','python/pyproject.toml','python/sglang/srt/models/glm5.py','python/sglang/srt/models/glm5_next.py']:
        fetch(f'https://raw.githubusercontent.com/sgl-project/sglang/{ref}/{path}',OUT/'sglang-v0.5.20'/path)
