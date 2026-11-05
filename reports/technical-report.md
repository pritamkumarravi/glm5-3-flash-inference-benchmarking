# GLM-5.3-Flash on sixteen H100s: technical research report

Generated 2026-11-04T10:33:01.520334+00:00. Only completed, accepted measurements appear below. Both rental
SSH endpoints became unreachable before the scheduled removal time. The final
PD-plus-HiCache startup failed, and its planned64K/c128 experiment did not run.
Untested configurations have no inferred performance numbers.

## Hardware, software and provenance

Two isolated research Kubernetes nodes each provide eight H100 80GB HBM3 GPUs,
NVLink within the node, and about 1.5 TiB system RAM. The inter-node fabric is
native InfiniBand, not RoCE. Provider Kubernetes, GPU runtime and networking
configuration were not overwritten. An isolated K3s v1.34.12+k3s1 installation
schedules the experiment through NVIDIA device-plugin v0.18.2.

The FP8 checkpoint is zai-org/GLM-5.3-Flash at immutable revision
46a050bec13002ad29ee795c16e61cf4fa3c4a9c. All 62 weight shards, 328,337,455,672 bytes,
were verified by SHA256 against Hugging Face LFS metadata on both nodes.
The pinned runtime is SGLang 0.5.20, PyTorch 2.13.0+cu130, CUDA 13.0, NCCL 2.29.7,
TileLang 0.1.12, sgl-deep-gemm 0.2.0, Dynamo 1.6.0, NIXL 1.5.0 and
Mooncake transfer engine 0.3.13. Runtime freezes and image evidence are preserved.
Dynamo's optional SGLang extra targets a different runtime version; the derived
image installs the pinned core packages while retaining SGLang 0.5.20. Functional
compatibility was tested against real weights rather than inferred from imports.

Both aggregated and PD workers use BF16 KV, TileLang DSA prefill/decode, DeepGemm,
TP8, CP1, no speculative decoding, and the checkpoint's default thinking behavior.
Dynamo uses explicit GLM45 reasoning and GLM47 tool parsers. FP8 weights occupy
about 37.98 GiB per GPU. The1,048,576-token context setting is a configured maximum;
it is not a claim that full-length concurrent requests fit in the measured pools.

## Method

CPU-only Kubernetes clients drive the official pinned SGLang serving benchmark
through OpenAI-compatible streaming completions. Source adapters handle empty SSE
chunks, preserve authoritative usage token counts, and omit a native-only cache
field rejected by Dynamo. Raw commands, runner sources, version metadata, per-request
timings, stdout/stderr and server metrics are preserved for every case. A completed
case is accepted only when every request succeeds and every output reaches its
requested length. Timing excludes post-run metadata retrieval.

Standard workloads use exact-length random token IDs. Cache workloads use64 prefix
groups, two requests per group,75% shared-prefix targets, seed42, and a cache flush
after eight warmups. The32768 input target produces4,367,048 actual input tokens
across128 requests (about34,118 per request) after generation and tokenization.
Use actual token counts for throughput. Reported input throughput counts all input
tokens, including reused tokens; it is not uncached prefill compute throughput.

These are exploratory single repetitions unless separate repetitions are shown.
No confidence intervals or long-duration stability conclusions are justified.
The user redirected the standard sweep to HiCache and PD; canceled cases are
excluded. Worker cache counters cover warmup plus measurement. Cache token counters
with TP rank labels use rank0 to avoid eightfold duplication. Backup counters may
aggregate physical transfers over all TP ranks; do not interpret them as logical
unique token counts or divide asynchronous duration counters into wall-clock GB/s.

## Accepted standard serving measurements

| Profile | GPUs | Input/output target | Client concurrency | Completed | Output tok/s | Tok/s/GPU | Mean TTFT s | P99 TTFT s | Mean TPOT ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fpm-ep1-l1 | 8 | 4096/1024 | 8 | 100 | 529.24 | 66.15 | 1.323 | 2.106 | 13.37 |
| fpm-ep1-l1 | 8 | 4096/1024 | 32 | 100 | 734.33 | 91.79 | 8.738 | 46.260 | 28.21 |
| fpm-ep1-l1 | 8 | 4096/1024 | 4 | 100 | 345.71 | 43.21 | 0.786 | 0.878 | 10.81 |
| cookbook-ep8-l1 | 8 | 4096/1024 | 8 | 100 | 601.93 | 75.24 | 1.324 | 2.077 | 11.55 |
| cookbook-ep8-l1 | 8 | 4096/1024 | 32 | 100 | 1126.24 | 140.78 | 4.125 | 21.894 | 17.92 |

The TP8/EP1 profile follows the user's FPM parallelism reference. TP8/EP8 follows
the H100 cookbook. The EP8 native run used memory fraction 0.75; EP1 used 0.70, and
they ran on different nodes. Differences cannot be attributed solely to EP.

## HiCache and PD cache-pressure comparisons

| Profile | GPUs | Input/output target | Client concurrency | Completed | Output tok/s | Tok/s/GPU | Mean TTFT s | P99 TTFT s | Mean TPOT ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dynamo-ep1-host32 | 8 | 32768/128 | 8 | 128 | 80.10 | 10.01 | 6.448 | 22.680 | 49.85 |
| dynamo-ep1-host64 | 8 | 32768/128 | 8 | 128 | 102.51 | 12.81 | 5.244 | 10.951 | 37.34 |
| dynamo-ep1-l1 | 8 | 32768/128 | 8 | 128 | 72.94 | 9.12 | 7.188 | 22.416 | 53.90 |
| pd-nixl | 16 | 32768/128 | 8 | 128 | 104.45 | 6.53 | 8.498 | 10.032 | 8.31 |
| pd-nixl | 16 | 32768/128 | 32 | 128 | 104.28 | 6.52 | 33.628 | 41.606 | 8.30 |

Aggregated rows allocate8 GPUs; PD rows allocate16. Per-GPU values prevent a
16-GPU deployment from being credited with scaling merely because it uses twice
the hardware. Each comparison requires matching input/output, concurrency and
prefix distributions. Single-prefill-worker PD validates cache-aware routing and
cache events but cannot measure routing-affinity benefits among multiple prefill
replicas. The blog's4P4D layout uses a much smaller Qwen checkpoint; this GLM
checkpoint requires a different per-role allocation on the same hardware budget.

## Cache capacity, observed reuse and memory

The host32 setting allocates per TP rank16.87 GiB for paged KV and15.13 GiB for
KDA state, about256 GiB across eight ranks. Host64 allocates33.74+30.26 GiB per
rank, about512 GiB across eight ranks. The logical KV host capacities are
1,497,856 and2,995,648 tokens respectively; those logical token capacities should
not be multiplied by TP degree. GPU memory fraction 0.70 gives the aggregated and
prefill roles708,736 paged-KV tokens plus 437 KDA state slots. The PD decode role
uses 96 KDA slots and1,296,448 paged-KV tokens at the same requested memory fraction.
These measured role-specific allocations show why the two pools must be tracked
separately. Decode has no host offloading in the PD cache experiment.

| Profile | Concurrency | Device-hit token delta | Host-hit token delta | Host KV tokens after |
|---|---:|---:|---:|---:|
| dynamo-ep1-host32 | 8 | 576640 | 518336 | 1497856 |
| dynamo-ep1-host64 | 8 | 562752 | 1034304 | 2995648 |
| dynamo-ep1-l1 | 8 | 575168 | 0 | 0 |
| pd-nixl | 8 | 603712 | 0 | 0 |
| pd-nixl | 32 | 604480 | 0 | 0 |

Host-hit counters verify actual reuse after host offloading. Dynamo does not
return the native per-request cache detail extension; placeholder zeroes in its
client cache report are not evidence of zero cache hits. The worker counters
are authoritative for these experiments. No L3 backend was configured or tested.

## Networking and PD correctness

The16-rank NCCL check passed rank-sum correctness over native InfiniBand/GDRDMA.
At256 MiB it measured 140.38 GB/s algorithm bandwidth and 263.22 GB/s normalized bus
bandwidth, 1.912 ms. A one-QP verbs check measured 371.94 Gb/s write bandwidth and
2.84 microseconds typical 8-byte latency. These are infrastructure measurements,
not inference or KV-transfer bandwidth results.

Kubernetes RDMA shared-device-plugin advertises rdma/ib but allocation fails on
provider-unavailable MAD device nodes. A nonprivileged /dev/infiniband hostPath
mount with IPC_LOCK opens all eight HCAs inside real worker containers. No provider
device nodes were fabricated and no privileged pod was required.

The NIXL PD real-weight gate passed arithmetic at concurrency 1, 8, 32, repeated-prefix
retrieval, and a forced tool call through Dynamo. Both roles use identical TP8,
no prefill CP and no speculation. UCX 1.23 logs show inter-node rma(rc_mlx5/mlx5_*:1)
connections during these requests. This is functional real-weight PD evidence;
it is not a full token-logit numerical parity test or broad quality evaluation.
The recorded HCA counter deltas corroborate data-plane activity where telemetry
coverage is available. TCP request/control-plane logs do not imply TCP KV transfer.
Mooncake PD and a controlled TCP-versus-RDMA comparison remain unmeasured.

## GPU and host telemetry

Samplers record utilization, VRAM, power, temperature, clocks, host/cgroup memory,
network and InfiniBand counters. NVIDIA-SMI memory utilization is a busy-time
measure, not achieved memory bandwidth or SM occupancy. No achieved HBM bandwidth
or detailed SM-utilization claim is made.

The original samplers exited on an unhandled10-second NVIDIA-SMI timeout during
worker replacement around10:06-10:07 UTC. Sampling was made timeout-resilient and
restarted around10:15 UTC. Early PD telemetry is incomplete. Coverage is reported
per node; averages with partial coverage are not full-run utilization estimates.
Cgroup memory includes checkpoint page cache and other research components, not
only HiCache. Raw inference and worker metrics remain available across this gap.

| Profile | C | Node | GPU utilization % | Mean power W/GPU | Peak VRAM MiB/GPU | Approx. window coverage % | IB transmit GiB in observed span |
|---|---:|---|---:|---:|---:|---:|---:|
| dynamo-ep1-host32 | 8 | node0 | 73.0 | 403.3 | 62334 | 98.7 | 0.00 |
| dynamo-ep1-host64 | 8 | node1 | 84.7 | 435.6 | 62398 | 98.5 | 0.00 |
| dynamo-ep1-l1 | 8 | node1 | 74.6 | 414.4 | 62228 | 98.6 | 0.00 |
| pd-nixl | 32 | node0 | 87.7 | 506.4 | 65453 | 97.3 | 428.83 |
| pd-nixl | 32 | node1 | 81.2 | 221.0 | 64787 | 97.8 | 0.54 |

## Best observed configurations and next optimizations

- aggregated standard throughput: **cookbook-ep8-l1**, concurrency32, 1126.24 output tok/s, mean TTFT4.125s. Evidence: `benchmarks/exported/node1/raw/cookbook-ep8-l1/20261104T092909.794065Z-A-i4096-o1024-c32-prefix0.0-rep0`.
- aggregated standard latency: **fpm-ep1-l1**, concurrency4, 345.71 output tok/s, mean TTFT0.786s. Evidence: `benchmarks/exported/node0/raw/fpm-ep1-l1/20261104T093715.187379Z-A-i4096-o1024-c4-prefix0.0-rep0`.
- aggregated hicache at c8: **dynamo-ep1-host64**, concurrency8, 102.51 output tok/s, mean TTFT5.244s. Evidence: `benchmarks/exported/node1/raw/dynamo-ep1-host64/20261104T095940.668239Z-D-i32768-o128-c8-prefix0.75-rep0`.
- pd at c8: **pd-nixl**, concurrency8, 104.45 output tok/s, mean TTFT8.498s. Evidence: `benchmarks/exported/node1/raw/pd-nixl/20261104T101136.508635Z-D-i32768-o128-c8-prefix0.75-rep0`.
- pd at c32: **pd-nixl**, concurrency32, 104.28 output tok/s, mean TTFT33.628s. Evidence: `benchmarks/exported/node1/raw/pd-nixl/20261104T101537.254098Z-D-i32768-o128-c32-prefix0.75-rep0`.

The latency selection spans the tested concurrency points and is not evidence of
an engine improvement at a fixed offered load. These are observed candidates for
the requested low-latency and high-throughput profiles; speculative/MTP profiles
were not validated. A sixteen-GPU, two-replica aggregated comparison remains needed
before declaring PD the more efficient architecture for this hardware budget.

The next useful experiments are repeated matched-load trials, prefill EP8 versus
EP1 under PD with its own correctness gate, longer-lived prefix reuse distributions,
and write_back versus write_through with observed host reloads and scheduling costs.
The requested blog uses write_back for its Qwen workload. This experiment starts
from the already measured write_through hybrid-model path; the blog's policy
recommendation is not treated as a measured GLM result. Higher memory fractions
and max-running requests require fresh KV/KDA capacity and graph-workspace checks.
At high client concurrency, inspect admission queues and per-role power/compute
before interpreting NVIDIA-SMI busy percentages as productive model compute.

## Failures, incomplete work and interpretation limits

PD plus HiCache allocated its host pools but failed its separate startup gate:
`NIXL create_backend('UCX', dict(num_threads=8)) did not return within60s`.
See `logs/prefill/nixl-host64-failed-previous.log`. Startup also warned that
accelerated IB support was not found. Node1 became NotReady and SSH exports failed;
node0 later also became unreachable. The relationship between the UCX startup
failure and the network outage is unresolved. No PD-plus-HiCache throughput,
correctness, or64K/c128 capacity result is claimed. Aggregate HiCache and baseline
NIXL PD results above completed before this failure.

- Early clients tried an offline ShareGPT download, indexed empty SSE chunks, or
  supplied unsupported Dynamo cache extensions. These runs failed and are excluded.
- A too-small64-token thinking budget cut off correctness answers. The checkpoint's
  chat template appends a thinking prefix; the gate uses 512 tokens instead.
- An EP1 c16 standard run lost post-run service metadata around a worker restart.
  The original restart cause was not established. It has no accepted result.
- Initial GPU device-plugin socket-path and RDMA-plugin registration issues were
  resolved in isolated research manifests; provider configuration was retained.
- An API TLS timeout interrupted a PD transition. A coordinator process overlap
  also interrupted the aggregate host64 post-run semantic gate. That gate is not
  claimed as passed. Both cache throughput jobs completed their output gates.
- Baseline PD correctness passed before its benchmark. PD plus HiCache has a
  separate gate; its status and accepted measurements must be checked independently.
- No artificial GPU stress tests were used. No unsupported Blackwell command was
  taken as proof of H100 compatibility.
- Full1M serving, MTP, alternative CP/EP sweeps, L3 recovery, and the complete original
  benchmark matrix remain unmeasured. Missing cases have no estimated results.

## Reproduction and artifact preservation

See environment/runtime-lock.json, the pinned Dockerfile under configs/tuning,
and the complete command arrays in benchmark metadata. Apply the immutable scripts
ConfigMap referenced by each Job. Node-local model PVs survive pod replacement
but not rental deletion; redownload and verify the exact revision on new rentals.
Image aliases are preloaded in the isolated containerd; reproduce the pinned build
and import before applying manifests. Images do not use the latest tag.

Aggregated manifests are under kubernetes/aggregated-*.json. PD baseline is
kubernetes/pd-nixl.json, frontend kubernetes/dynamo-frontend-pd.json, and prefill-only
host64 offloading kubernetes/pd-nixl-host64.json. The sequence script gates every
performance stage on preceding completion and host64 runtime readiness. Concurrency
is the client admission pressure; worker max-running is 32 in the matched profiles.
Larger client concurrency does not imply 128 simultaneous resident 64K sequences.

The local workspace is outside the rented nodes. Continuous rsync exports logs,
raw requests/results, configurations and monitoring. Git preserves code/configuration;
raw data and secrets are excluded from Git. Credentials are excluded from exports.
Raw artifact paths appear in benchmarks/processed/accepted.json, alongside failures
in failed.json. Re-run summarize-results.py then write-report.py after each export.

## Sources

- [Official H100/model cookbook](https://github.com/sgl-project/sglang/blob/851642ade7d02002cf6c73a43a22987ba7511a4b/docs/cookbook/autoregressive/GLM/GLM-5.3-Flash.mdx)
- [Pinned SGLang 0.5.20 source](https://github.com/sgl-project/sglang/tree/94602c9c2b7cbdb8efd5c52802dac6a1c180089e)
- [Dynamo source inspected](https://github.com/ai-dynamo/dynamo/tree/73014901d4e7610358fcf28535418ba9c5f50812)
- [Requested blog and companion manifests](https://github.com/Prasannajaga/deployment-guide/tree/ce2a42a32f7eae5a8734e07e271eb4b7bb012360/models/qwen3.6-35B-A3B/sglang/disagg/tp1-ep2-4p4d)
