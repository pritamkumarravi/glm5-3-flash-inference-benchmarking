# Infrastructure discovery — 2026-11-04 UTC

Measured inside the two Lium rental containers, before deployment changes.

| Capability | Node 0 | Node 1 |
|---|---|---|
| Lium identifier | brave-raven-1a | eager-fox-e8 |
| Overlay address | 10.42.0.1 | 10.42.0.2 |
| GPU inventory | 8 H100 80GB HBM3, SM90 | 8 H100 80GB HBM3, SM90 |
| Memory per GPU | 81,559 MiB | 81,559 MiB |
| Intra-node links | NV18 all GPU pairs | NV18 all GPU pairs |
| Driver | 580.173.02 | 580.173.02 |
| Preinstalled PyTorch | 2.12.0+cu130 | 2.12.0+cu130 |
| PyTorch CUDA / NCCL | 13.0 / 2.29.7 | 13.0 / 2.29.7 |
| CPU | Xeon Platinum 8468, 128 logical CPUs | same |
| NUMA | 2 domains | 2 domains |
| Visible RAM | ~1.5 TiB | ~1.5 TiB |
| cgroup memory limit | 1,639,603,765,248 bytes | same |
| /root storage | XFS loop mount, ~1.6 TiB free | same |
| Docker data storage | ~420 GiB free | ~416 GiB free |
| Existing rental Docker workloads | none | none |
| Existing accessible Kubernetes | no binaries/config/cluster found | same |
| InfiniBand | mlx5_0 through mlx5_7, ACTIVE, 400 Gb/s links | same |
| GPUDirect prerequisite | nvidia_peermem loaded, unlimited memlock | same |

The 10.42.0.x overlay is WireGuard (MTU 1420), used for bootstrap/control.
Native InfiniBand verbs devices are exposed inside both containers. This is
InfiniBand, not the deployment guide's RoCE fabric; its Ethernet GID/IPAM
settings do not apply.

Twenty ICMP samples per direction measured mean overlay RTTs of 0.943 ms
(node 0 to node 1) and 1.010 ms (reverse), with no packet loss.

A bounded 16-rank PyTorch/NCCL test passed a rank-sum correctness check.
NCCL selected IB and logged NET/IB/GDRDMA data channels on both nodes.
Twenty measured iterations after five warmups, maximum rank elapsed time:

| Buffer | All-reduce latency | Algorithm GB/s | Normalized bus GB/s |
|---|---:|---:|---:|
| 1 MiB | 0.09466 ms | 11.08 | 20.77 |
| 16 MiB | 0.41613 ms | 40.32 | 75.59 |
| 256 MiB | 1.91214 ms | 140.38 | 263.22 |

These are one bounded diagnostic run, not final communication benchmarks or
inference throughput. Only the preliminary rank-sum buffer is checked for
numerical correctness; timed buffers contain zeros. The normalized bus metric
uses the conventional 2*(world-1)/world factor and is not single-NIC bandwidth.

perftest 6.20 on mlx5_0, native IB RC, host buffers, one QP:
8 MiB RDMA writes over five seconds measured 371.94 Gb/s (~46.49 GB/s).
8-byte send latency over 10,000 iterations measured typical 2.84 us,
mean 2.86 us, client p99 3.47 us. This is not KV transfer or GPU-buffer latency.
The perftest 'Data ex. method: Ethernet' line describes its TCP control handshake;
its transport and link type were IB and its data path used exchanged LIDs/QPs.

Kubernetes GPU/RDMA scheduling, operators, storage classes, PVCs and CRDs are
unverified because no accessible Kubernetes control plane exists in the rentals.
Docker is local to each rental; provider-managed services have not been modified.
The empty /var/lib/k0s and rancher directories are sysbox-provided mount points,
not evidence of a running cluster. Rental storage persistence after termination
has not been established. Research artifacts are captured on the local Mac.

Both rentals are scheduled for removal at 10:36 UTC. No extension is authorized.

Raw evidence is under logs/infrastructure/*node-discovery, *boundary-discovery,
*nccl-16gpu and *rdma-verbs. Commands and timestamps are in research-log.md.
