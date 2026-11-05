#!/usr/bin/env bash
set -euo pipefail
image='lmsysorg/sglang@sha256:b27fce60bc5494c118c4910702812bcfa8cee67abcdd1ff8b0902f21647552f4'
printf 'timestamp=%s image=%s\n' "$(date -u +%FT%TZ)" "$image"
docker pull "$image"
docker image inspect "$image" --format '{{json .RepoDigests}} {{json .Config.Labels}}'
docker run --rm --gpus all --entrypoint python3 "$image" -c 'import importlib.metadata as m; import torch; print({k:m.version(k) for k in ["sglang","torch","transformers","tilelang","sgl-deep-gemm"]}); print("cuda",torch.version.cuda,"nccl",torch.cuda.nccl.version(),"devices",torch.cuda.device_count()); x=torch.ones(8,device="cuda"); print("gpu_test",x.sum().item())'
