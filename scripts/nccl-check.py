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
