#!/usr/bin/env bash
set -euo pipefail
root=/root/glm53-research
mkdir -p "$root/scripts" "$root/model-cache" "$root/logs/infrastructure"
cat > "$root/scripts/download-model.py" <<'GLM53_DOWNLOAD_PY'
#!/usr/bin/env python3
"""Download and verify the exact real FP8 checkpoint into a retained local PV."""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import time
from huggingface_hub import HfApi, snapshot_download

MODEL='zai-org/GLM-5.3-Flash'
REVISION='46a050bec13002ad29ee795c16e61cf4fa3c4a9c'
DEST=Path('/cache/checkpoint')
DEST.mkdir(parents=True,exist_ok=True)
start=time.monotonic()
info=HfApi().model_info(MODEL,revision=REVISION,files_metadata=True)
assert info.sha==REVISION
weights=[s for s in info.siblings if s.rfilename.endswith('.safetensors')]
expected=sum(s.size for s in weights)
existing=sum(p.stat().st_size for p in DEST.glob('*.safetensors'))
assert shutil.disk_usage(DEST).free + existing > expected+50*(1<<30),'Insufficient storage headroom'
print(json.dumps(dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),model=MODEL,revision=REVISION,weight_files=len(weights),expected_weight_bytes=expected)),flush=True)
snapshot_download(MODEL,revision=REVISION,local_dir=str(DEST),max_workers=8)
config=json.loads((DEST/'config.json').read_text())
assert config['model_type']=='glm5_next'
assert config['quantization_config']['quant_method']=='fp8'
assert config['quantization_config']['weight_block_size']==[128,128]
def verify(s):
    p=DEST/s.rfilename
    assert p.stat().st_size==s.size,(p,'size mismatch')
    expected_sha=s.lfs.sha256 if s.lfs else None
    assert expected_sha,(p,'missing LFS checksum')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(16<<20),b''):h.update(chunk)
    actual=h.hexdigest()
    assert actual==expected_sha,(p,'checksum mismatch')
    print('VERIFIED',s.rfilename,s.size,actual,flush=True)
    return dict(file=s.rfilename,bytes=s.size,sha256=actual)
with ThreadPoolExecutor(max_workers=4) as pool:
    verified=list(pool.map(verify,weights))
manifest=dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),model=MODEL,revision=REVISION,elapsed_seconds=time.monotonic()-start,files=verified,verified_weight_bytes=expected)
(DEST.parent/'download-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Path('/logs/model-download-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('MODEL_VERIFIED',REVISION,expected,'elapsed_seconds',time.monotonic()-start,flush=True)
GLM53_DOWNLOAD_PY
image='lmsysorg/sglang@sha256:b27fce60bc5494c118c4910702812bcfa8cee67abcdd1ff8b0902f21647552f4'
if docker inspect glm53-model-download >/dev/null 2>&1; then
  docker inspect glm53-model-download --format '{{.State.Status}} {{.State.ExitCode}}'
  exit 0
fi
docker run -d --name glm53-model-download --runtime runc --cpus 8 --memory 64g \
  -e NVIDIA_VISIBLE_DEVICES=void -e HF_HOME=/cache/hf -e HF_XET_HIGH_PERFORMANCE=1 \
  -v "$root/model-cache:/cache" \
  -v "$root/scripts/download-model.py:/research/download-model.py:ro" \
  -v "$root/logs/infrastructure:/logs" \
  --entrypoint bash "$image" -lc 'set -o pipefail; python3 -u /research/download-model.py 2>&1 | tee /logs/model-download.log'
