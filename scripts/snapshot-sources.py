#!/usr/bin/env python3
"""Archive upstream documentation and code at immutable repository commits."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]/'environment/sources'
ROOT.mkdir(parents=True,exist_ok=True)
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'glm53-research-readonly'})
    with urllib.request.urlopen(req,timeout=45) as r:
        return r.read()

repos={
 'sgl-project/sglang':[
  'docs/cookbook/autoregressive/GLM/GLM-5.3-Flash.mdx',
  'docs/advanced_features/hierarchical_cache.md',
  'python/sglang/srt/server_args.py',
  'python/sglang/srt/disaggregation/nixl/conn.py',
 ],
 'ai-dynamo/dynamo':['README.md','pyproject.toml'],
 'Prasannajaga/deployment-guide':['README.md','cluster.md','setup.md','pod-native-roce.md','model-caching.md'],
}
index=[]
for repo,paths in repos.items():
    try:
        commit=json.loads(get(f'https://api.github.com/repos/{repo}/commits/main'))['sha']
        dest=ROOT/repo.replace('/','--')/commit
        dest.mkdir(parents=True,exist_ok=True)
        tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
        (dest/'tree.json').write_text(json.dumps(tree,indent=2))
        available={x['path'] for x in tree['tree'] if x['type']=='blob'}
        if repo=='sgl-project/sglang':
            paths += sorted(p for p in available if ('glm-5.3-flash' in p.lower() and p.endswith(('.jsx','.json'))) or ('hicache' in p.lower() and p.endswith('.md')))
        if repo=='ai-dynamo/dynamo':
            paths += sorted(p for p in available if ('glm-5.3' in p.lower() or 'glm_5_3' in p.lower()) and p.endswith(('.md','.yaml','.yml','.sh','.toml')))
        if repo=='Prasannajaga/deployment-guide':
            paths += sorted(p for p in available if ('glm' in p.lower()) and p.endswith(('.yaml','.yml','.md','.sh')))
        for path in dict.fromkeys(paths):
            if path not in available:
                print('NOT_FOUND',repo,path,flush=True)
                continue
            url=f'https://raw.githubusercontent.com/{repo}/{commit}/{path}'
            body=get(url)
            out=dest/path
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_bytes(body)
            index.append(dict(repository=repo,commit=commit,path=path,url=url,sha256=hashlib.sha256(body).hexdigest(),fetched_at=dt.datetime.now(dt.timezone.utc).isoformat()))
            print('SAVED',repo,commit,path,len(body),flush=True)
    except Exception as e:
        print('ERROR',repo,type(e).__name__,str(e),flush=True)
(ROOT/'index.json').write_text(json.dumps(index,indent=2)+'\n')
if len({x['repository'] for x in index})!=len(repos):
    raise SystemExit(1)
