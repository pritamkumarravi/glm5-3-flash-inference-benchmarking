#!/usr/bin/env bash
set -euo pipefail
image='lmsysorg/sglang@sha256:b27fce60bc5494c118c4910702812bcfa8cee67abcdd1ff8b0902f21647552f4'
alias='glm53/sglang:0.5.20-cu130-b27fce60'
docker tag "$image" "$alias"
docker save "$alias" | /root/glm53-research/bin/k3s ctr images import -
/root/glm53-research/bin/k3s ctr images ls | grep glm53
