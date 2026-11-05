#!/usr/bin/env bash
set -euo pipefail
root=/root/glm53-research
mount_dir="$root/image-unpack"
mkdir -p "$mount_dir"
"$root/bin/k3s" ctr images mount docker.io/glm53/sglang:0.5.20-cu130-b27fce60 "$mount_dir"
"$root/bin/k3s" ctr images unmount "$mount_dir"
"$root/bin/k3s" ctr images check | grep glm53
