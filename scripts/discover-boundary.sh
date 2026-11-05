#!/usr/bin/env bash
set -u
export LC_ALL=C
run() {
  printf '\n### %s | ' "$(date -u +%FT%TZ)"
  printf '%q ' "$@"
  printf '\n'
  timeout 45 "$@" 2>&1
  printf '\nexit_code=%s\n' "$?"
}
run bash -c 'for x in kubectl k3s k0s kubeadm docker containerd ctr crictl mpirun all_reduce_perf ib_write_bw ib_read_bw ib_send_lat iperf3 ucx_info python python3 curl wget capsh; do command -v "$x" || true; done'
run docker version
run docker info
run docker ps -a --format '{{.ID}} {{.Image}} {{.Names}} {{.Status}}'
run docker image ls --digests
run bash -c 'for x in /var/lib/k0s /var/lib/rancher/k3s /var/lib/rancher/rke2 /var/lib/kubelet /etc/kubernetes /run/secrets/kubernetes.io/serviceaccount /var/run/secrets/kubernetes.io/serviceaccount; do if test -d "$x"; then echo "$x"; ls -ld "$x"; find "$x" -maxdepth 1 -mindepth 1 -printf "%f\n" | head -15; fi; done'
run bash -c 'for p in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.high /sys/fs/cgroup/cpu.max /sys/fs/cgroup/cpuset.cpus.effective /sys/fs/cgroup/memory/memory.limit_in_bytes; do test ! -f "$p" || { echo "$p"; cat "$p"; }; done'
run capsh --print
run bash -c 'for p in /root /workspace /var/lib/docker /var/lib/k0s; do findmnt -T "$p" -o TARGET,SOURCE,FSTYPE,SIZE,AVAIL,OPTIONS; done'
run bash -c 'for f in /sys/class/infiniband/*/ports/*/state /sys/class/infiniband/*/ports/*/rate /sys/class/infiniband/*/ports/*/link_layer; do echo "$f"; cat "$f"; done'
run bash -c 'lsmod | grep -E "nvidia_peermem|nv_peer_mem|mlx5|ib_core"'
run bash -c 'python3 -m pip list --format=freeze | grep -Ei "torch|sglang|dynamo|nccl|nixl|mooncake|triton|tilelang|deep.gemm|cuda|transformers|huggingface"'
run python3 -c 'import os,resource; print("memlock",resource.getrlimit(resource.RLIMIT_MEMLOCK)); print("kubernetes_env_keys",[k for k in os.environ if k.startswith("KUBERNETES_")]); print("kubeconfig_set",bool(os.environ.get("KUBECONFIG")))'
run bash -c 'if ip -4 addr show wg0 | grep -q 10.42.0.1/; then ping -c 20 -i 0.1 -W 2 10.42.0.2; else ping -c 20 -i 0.1 -W 2 10.42.0.1; fi'
run bash -c 'curl -sSI --max-time 15 https://huggingface.co; curl -sSI --max-time 15 https://pypi.org'
