#!/usr/bin/env bash
set -euo pipefail
mkdir -p /root/glm53-research/scripts
cd /root/glm53-research
cat > scripts/nccl-check.py <<'GLM53_NCCL_PY'
#!/usr/bin/env python3
"""Bounded 16-GPU communication correctness and all-reduce timing check."""
import datetime
import json
import os
import time
import torch
import torch.distributed as dist

local_rank = int(os.environ['LOCAL_RANK'])
torch.cuda.set_device(local_rank)
dist.init_process_group('nccl', timeout=datetime.timedelta(seconds=120), device_id=torch.device('cuda',local_rank))
rank, world = dist.get_rank(), dist.get_world_size()
if rank == 0:
    print(json.dumps(dict(torch=torch.__version__, cuda=torch.version.cuda, nccl=torch.cuda.nccl.version(), world=world)),flush=True)
probe=torch.full((4096,),rank+1,dtype=torch.float32,device='cuda')
dist.all_reduce(probe)
assert torch.all(probe == world*(world+1)/2).item(), 'all_reduce correctness failed'
for nbytes in [1<<20,16<<20,256<<20]:
    x=torch.zeros(nbytes//4,dtype=torch.float32,device='cuda')
    for _ in range(5):
        dist.all_reduce(x)
    torch.cuda.synchronize()
    dist.barrier()
    t=time.perf_counter()
    iterations=20
    for _ in range(iterations):
        dist.all_reduce(x)
    torch.cuda.synchronize()
    elapsed=torch.tensor([time.perf_counter()-t],device='cuda',dtype=torch.float64)
    dist.all_reduce(elapsed,op=dist.ReduceOp.MAX)
    seconds=elapsed.item()/iterations
    if rank == 0:
        alg=nbytes/seconds/1e9
        print(json.dumps(dict(bytes=nbytes,iterations=iterations,latency_ms=seconds*1000,algorithm_GBps=alg,bus_GBps=alg*2*(world-1)/world,correctness='passed')),flush=True)
dist.destroy_process_group()
GLM53_NCCL_PY
export OMP_NUM_THREADS=2
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=INIT,NET,GRAPH
export NCCL_SOCKET_IFNAME='=wg0'
export GLOO_SOCKET_IFNAME=wg0
if ip -4 addr show wg0 | grep -q 10.42.0.1/; then
  rank=0
else
  rank=1
fi
printf 'timestamp=%s rank=%s\n' "$(date -u +%FT%TZ)" "$rank"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu,power.draw --format=csv
timeout 300 python3 -m torch.distributed.run --nproc_per_node=8 --nnodes=2 --node_rank="$rank" --master_addr=10.42.0.1 --master_port=29500 scripts/nccl-check.py
