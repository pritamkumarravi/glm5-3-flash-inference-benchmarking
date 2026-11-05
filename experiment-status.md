# Experiment status

Updated 2026-11-04 10:33 UTC. Research is in progress; the rentals are scheduled
for removal at 10:36 UTC. No rental extension has been requested or made.

| Phase | Verified status |
|---|---|
| Hardware | 16 H100 80GB; NVLink within each node; about 1.5 TiB RAM per node |
| Network | Native InfiniBand; 16-rank NCCL correctness and bandwidth checks passed |
| Kubernetes | Isolated K3s v1.34.12+k3s1; both nodes Ready; GPU scheduling validated |
| RDMA in containers | Nonprivileged verbs hostPath opens all 8 HCAs per node; RDMA plugin allocation fails on unavailable provider MAD devices |
| Model | Immutable FP8 revision 46a050bec13002ad29ee795c16e61cf4fa3c4a9c, all 62 shards SHA256 verified on both nodes |
| Runtime | SGLang 0.5.20, CUDA 13.0, PyTorch 2.13.0, NCCL 2.29.7; pinned derived Dynamo 1.6.0 / NIXL 1.5.0 image |
| Aggregated baseline | Real-weight correctness and accepted TP8/EP1 and TP8/EP8 measurements exist |
| Dynamo integration | Real-weight arithmetic at concurrency 1/8/32, prefix retrieval, and forced tool call passed through frontend |
| HiCache | L1, host32 and host64 completed128/128 requests; host64 best first-run throughput102.51 output tok/s versus L1 72.94 |
| PD | NIXL TP8 per role passed real-weight correctness; c8/c32 pressure completed128/128; about104 output tok/s; inter-node UCX rc_mlx5 and substantial IB traffic verified |
| PD + HiCache | Host pools allocated, then NIXL UCX backend creation timed out; correctness gate not reached; no benchmark or64K/c128 result |
| Availability | Node1 NotReady/SSH timeout; node0 SSH later timed out. Current live serving unavailable; no provider configuration changed |
| Backup | Verified local archive created10:31:22UTC,1141 files; further exports retrying |
| L3 | Not configured or tested |
| Preservation | Continuous rsync to this local workspace, node telemetry, immutable client ConfigMaps, complete container log generations |

Accepted measurements require all requests completed and every output reached
the requested token count. See benchmarks/processed/accepted.json and the raw
artifact paths within it. Worker cache counters span warmup plus the timed run;
GPU telemetry is restricted to the recorded timed measurement window.

The standard sweep was stopped when the user prioritized HiCache and PD. Failed
client protocol attempts and interrupted/incomplete measurements remain in raw
artifacts and must not be treated as accepted throughput results.
