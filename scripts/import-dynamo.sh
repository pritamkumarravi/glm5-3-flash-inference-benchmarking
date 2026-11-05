#!/usr/bin/env bash
set -euo pipefail
docker image inspect glm53/sglang-dynamo:0.5.20-1.6.0 --format '{{.Id}}'
docker save glm53/sglang-dynamo:0.5.20-1.6.0 | /root/glm53-research/bin/k3s ctr images import -
/root/glm53-research/bin/k3s ctr images check | grep glm53/sglang-dynamo
