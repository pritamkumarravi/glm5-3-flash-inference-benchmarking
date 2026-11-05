#!/usr/bin/env bash
set -euo pipefail
root=/root/glm53-research/build/dynamo
mkdir -p "$root"
cat > "$root/Dockerfile.dynamo" <<'GLM53_BUILD_FILE'
FROM lmsysorg/sglang@sha256:b27fce60bc5494c118c4910702812bcfa8cee67abcdd1ff8b0902f21647552f4
COPY runtime-constraints.txt /opt/research/runtime-constraints.txt
RUN python3 -m pip install --no-cache-dir --constraint /opt/research/runtime-constraints.txt ai-dynamo==1.6.0 'nixl[cu13]==1.5.0' blake3==1.0.8
RUN python3 -m pip freeze > /opt/research/runtime-freeze.txt
RUN python3 -c 'import importlib.metadata as m; assert m.version("sglang")=="0.5.20"; import dynamo.sglang; print("Dynamo SGLang import passed")'
LABEL research.sglang.version="0.5.20" research.dynamo.version="1.6.0" research.base.amd64-manifest="sha256:b27fce60bc5494c118c4910702812bcfa8cee67abcdd1ff8b0902f21647552f4"
GLM53_BUILD_FILE
cat > "$root/runtime-constraints.txt" <<'GLM53_BUILD_FILE'
sglang==0.5.20
torch==2.13.0+cu130
transformers==5.12.1
tilelang==0.1.12
sgl-deep-gemm==0.2.0
GLM53_BUILD_FILE
docker build --progress plain -f "$root/Dockerfile.dynamo" -t glm53/sglang-dynamo:0.5.20-1.6.0 "$root"
