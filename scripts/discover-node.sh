#!/usr/bin/env bash
# Read-only inspection of the rented container/host boundary; no installs.
set -u
export LC_ALL=C
run() {
  printf '\n### %s | ' "$(date -u +%FT%TZ)"
  printf '%q ' "$@"
  printf '\n'
  timeout 40 "$@" 2>&1
  rc=$?
  printf '\nexit_code=%s\n' "$rc"
}
run hostname
run id
run uname -a
run cat /etc/os-release
run cat /proc/1/cgroup
run sh -c 'command -v systemctl && systemctl is-system-running'
run nvidia-smi
run nvidia-smi --query-gpu=index,name,uuid,memory.total,memory.used,driver_version,pci.bus_id,compute_cap --format=csv
run nvidia-smi topo -m
run nvidia-smi nvlink --status
run nvidia-smi -q
run nvcc --version
run lscpu
run numactl --hardware
run free -h
run lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
run df -hT
run findmnt
run ip -br addr
run ip route
run ip -d link
run ip route get 10.42.0.1
run ip route get 10.42.0.2
run ibv_devices
run ibv_devinfo
run ibstat
run ibdev2netdev
run rdma link
run rdma system show
run sh -c 'ls -la /dev/infiniband /sys/class/infiniband; for f in /sys/class/infiniband/*/ports/*/{state,rate,link_layer}; do test ! -f "$f" || { echo "$f"; cat "$f"; }; done'
run sh -c 'lsmod | rg "nvidia_peermem|nv_peer_mem|mlx5|ib_core"'
run sh -c 'command -v kubectl k3s kubeadm docker containerd ctr crictl mpirun all_reduce_perf ib_write_bw ib_read_bw ib_send_lat iperf3 ucx_info python python3'
run sh -c 'for p in /root/.kube/config /etc/kubernetes/admin.conf /etc/rancher/k3s/k3s.yaml /var/run/docker.sock /run/containerd/containerd.sock; do test ! -e "$p" || ls -ld "$p"; done'
run kubectl version -o json --request-timeout=15s
run kubectl get nodes -o wide --request-timeout=15s
run kubectl get pods -A -o wide --request-timeout=15s
run kubectl describe nodes --request-timeout=15s
run kubectl get daemonsets -A --request-timeout=15s
run kubectl get storageclasses,persistentvolumes --request-timeout=15s
run kubectl get persistentvolumeclaims -A --request-timeout=15s
run kubectl get crds --request-timeout=15s
run sh -c 'python3 -m pip list --format=freeze | rg -i "torch|sglang|dynamo|nccl|nixl|mooncake|triton|tilelang|deep.gemm|cuda|transformers|huggingface"'
run python3 -c 'import torch; print("torch",torch.__version__,"cuda",torch.version.cuda,"nccl",torch.cuda.nccl.version(),"devices",torch.cuda.device_count()); print("distributed",torch.distributed.is_available())'
run sh -c 'ls -ld /workspace /models /data /root/.cache/huggingface/hub /usr/local/cuda /opt/venv; ps -eo pid,comm,pcpu,pmem --sort=-pcpu | head -25'
