# Research log

All timestamps are UTC. Initial local discovery found Lium CLI and kubectl;
no local ~/.kube directory. The first sandboxed `lium ps --format json`
returned api_timeout / ConnectionError. Retrying with network permission.
No remote configuration changes or deployments have been made.

- 2026-11-04T08:19:19.727221+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/discover-node.sh` | exit 0 | [logs/infrastructure/20261104T081919.727221Z-node-discovery](logs/infrastructure/20261104T081919.727221Z-node-discovery) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:19:26.043091+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/discover-node.sh` | exit 0 | [logs/infrastructure/20261104T081926.043091Z-node-discovery](logs/infrastructure/20261104T081926.043091Z-node-discovery) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:20:05.875998+00:00 | local | `python3 scripts/snapshot-sources.py` | exit 0 | [logs/infrastructure/20261104T082005.875998Z-upstream-source-snapshot](logs/infrastructure/20261104T082005.875998Z-upstream-source-snapshot) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:21:03.311158+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/discover-boundary.sh` | exit 0 | [logs/infrastructure/20261104T082103.311158Z-boundary-discovery](logs/infrastructure/20261104T082103.311158Z-boundary-discovery) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:21:06.896147+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/discover-boundary.sh` | exit 0 | [logs/infrastructure/20261104T082106.896147Z-boundary-discovery](logs/infrastructure/20261104T082106.896147Z-boundary-discovery) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:22:23.996480+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/check-nccl.sh` | exit 0 | [logs/infrastructure/20261104T082223.996480Z-nccl-16gpu](logs/infrastructure/20261104T082223.996480Z-nccl-16gpu) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:22:26.885871+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/check-nccl.sh` | exit 0 | [logs/infrastructure/20261104T082226.885871Z-nccl-16gpu](logs/infrastructure/20261104T082226.885871Z-nccl-16gpu) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:28:22.408593+00:00 | local | `python3 scripts/inspect-metadata.py` | exit 0 | [logs/infrastructure/20261104T082822.408593Z-runtime-model-metadata](logs/infrastructure/20261104T082822.408593Z-runtime-model-metadata) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:31:11.560261+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/check-rdma.sh` | exit 0 | [logs/infrastructure/20261104T083111.560261Z-rdma-verbs](logs/infrastructure/20261104T083111.560261Z-rdma-verbs) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:31:13.340930+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/check-rdma.sh` | exit 0 | [logs/infrastructure/20261104T083113.340930Z-rdma-verbs](logs/infrastructure/20261104T083113.340930Z-rdma-verbs) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:35:08.361938+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/bootstrap-k3s.sh` | exit 1 | [logs/infrastructure/20261104T083508.361938Z-isolated-k3s-bootstrap](logs/infrastructure/20261104T083508.361938Z-isolated-k3s-bootstrap) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:35:08.361952+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/bootstrap-k3s.sh` | exit 0 | [logs/infrastructure/20261104T083508.361952Z-isolated-k3s-bootstrap](logs/infrastructure/20261104T083508.361952Z-isolated-k3s-bootstrap) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:36:08.801555+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/bootstrap-k3s.sh` | exit 0 | [logs/infrastructure/20261104T083608.801555Z-isolated-k3s-bootstrap-retry](logs/infrastructure/20261104T083608.801555Z-isolated-k3s-bootstrap-retry) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:37:51.717852+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/nvidia-device-plugin.yaml` | exit 0 | [logs/infrastructure/20261104T083751.717852Z-gpu-plugin-install](logs/infrastructure/20261104T083751.717852Z-gpu-plugin-install) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:35:51.934249+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/pull-runtime.sh` | exit 0 | [logs/infrastructure/20261104T083551.934249Z-pinned-runtime-pull](logs/infrastructure/20261104T083551.934249Z-pinned-runtime-pull) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:35:51.934168+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/pull-runtime.sh` | exit 0 | [logs/infrastructure/20261104T083551.934168Z-pinned-runtime-pull](logs/infrastructure/20261104T083551.934168Z-pinned-runtime-pull) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:47:00.936693+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/start-model-download.sh` | exit 0 | [logs/infrastructure/20261104T084700.936693Z-real-model-download-start](logs/infrastructure/20261104T084700.936693Z-real-model-download-start) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:47:00.936541+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/start-model-download.sh` | exit 0 | [logs/infrastructure/20261104T084700.936541Z-real-model-download-start](logs/infrastructure/20261104T084700.936541Z-real-model-download-start) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:41:58.444280+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/import-runtime.sh` | exit 0 | [logs/infrastructure/20261104T084158.444280Z-runtime-containerd-import](logs/infrastructure/20261104T084158.444280Z-runtime-containerd-import) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:41:58.444278+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/import-runtime.sh` | exit 0 | [logs/infrastructure/20261104T084158.444278Z-runtime-containerd-import](logs/infrastructure/20261104T084158.444278Z-runtime-containerd-import) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:47:34.522304+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/build-dynamo.sh` | exit 0 | [logs/infrastructure/20261104T084734.522304Z-dynamo-compatibility-build](logs/infrastructure/20261104T084734.522304Z-dynamo-compatibility-build) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:54:06.638272+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/aggregated-0-fpm-ep1-l1.json -f kubernetes/aggregated-1-cookbook-ep8-l1.json` | exit 0 | [logs/infrastructure/20261104T085406.638272Z-aggregated-baseline-deploy](logs/infrastructure/20261104T085406.638272Z-aggregated-baseline-deploy) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:51:42.957266+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/unpack-runtime.sh` | exit 0 | [logs/infrastructure/20261104T085142.957266Z-runtime-snapshot-unpack](logs/infrastructure/20261104T085142.957266Z-runtime-snapshot-unpack) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:51:42.957261+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/unpack-runtime.sh` | exit 0 | [logs/infrastructure/20261104T085142.957261Z-runtime-snapshot-unpack](logs/infrastructure/20261104T085142.957261Z-runtime-snapshot-unpack) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:59:23.826587+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/build-dynamo.sh` | exit 0 | [logs/infrastructure/20261104T085923.826587Z-dynamo-compatibility-build](logs/infrastructure/20261104T085923.826587Z-dynamo-compatibility-build) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:02:22.680439+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/rdma-device-plugin.yaml` | exit 0 | [logs/infrastructure/20261104T090222.680439Z-rdma-registration-path-fix](logs/infrastructure/20261104T090222.680439Z-rdma-registration-path-fix) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T08:59:23.826588+00:00 | brave-raven-1a | `lium exec brave-raven-1a --script scripts/import-dynamo.sh` | exit 0 | [logs/infrastructure/20261104T085923.826588Z-dynamo-image-import](logs/infrastructure/20261104T085923.826588Z-dynamo-image-import) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:01:04.059508+00:00 | eager-fox-e8 | `lium exec eager-fox-e8 --script scripts/import-dynamo.sh` | exit 0 | [logs/infrastructure/20261104T090104.059508Z-dynamo-image-import](logs/infrastructure/20261104T090104.059508Z-dynamo-image-import) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:13:07.428275+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/aggregated-0-fpm-ep1-l1.json` | exit 0 | [logs/infrastructure/20261104T091307.428275Z-ep1-probe-timeout-fix](logs/infrastructure/20261104T091307.428275Z-ep1-probe-timeout-fix) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:13:47.876122+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/bench-a-ep8.json` | exit 0 | [logs/infrastructure/20261104T091347.876122Z-benchmark-a-ep8-start](logs/infrastructure/20261104T091347.876122Z-benchmark-a-ep8-start) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:14:58.786631+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/rdma-device-plugin.yaml` | exit 0 | [logs/infrastructure/20261104T091458.786631Z-rdma-legacy-registration](logs/infrastructure/20261104T091458.786631Z-rdma-legacy-registration) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:18:06.740330+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/rdma-validation.json` | exit 0 | [logs/infrastructure/20261104T091806.740330Z-pod-rdma-validation](logs/infrastructure/20261104T091806.740330Z-pod-rdma-validation) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:20:37.617858+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/bench-a-ep8-offline.json` | exit 0 | [logs/infrastructure/20261104T092037.617858Z-benchmark-a-ep8-offline-start](logs/infrastructure/20261104T092037.617858Z-benchmark-a-ep8-offline-start) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:20:50.166634+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/bench-a-ep1.json` | exit 0 | [logs/infrastructure/20261104T092050.166634Z-benchmark-a-ep1-start](logs/infrastructure/20261104T092050.166634Z-benchmark-a-ep1-start) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:29:01.544543+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/bench-a-ep1-sse-fixed.json` | exit 0 | [logs/infrastructure/20261104T092901.544543Z-benchmark-a-ep1-sse-fixed](logs/infrastructure/20261104T092901.544543Z-benchmark-a-ep1-sse-fixed) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:32:44.092911+00:00 | Both native profiles passed real-weight arithmetic at concurrency 1/8/32, prefix retrieval (512-token output budget), and tool parsing. RDMA device-plugin claims failed on missing provider MAD devices; nonprivileged explicit verbs mounts opened all eight HCAs on both Kubernetes nodes. No provider device nodes were created.

- 2026-11-04T09:32:41.784092+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/aggregated-1-fpm-ep1-l1.json` | exit 0 | [logs/infrastructure/20261104T093241.784092Z-dynamo-worker-l1-deploy](logs/infrastructure/20261104T093241.784092Z-dynamo-worker-l1-deploy) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:49:32.721832+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml patch job bench-a-ep1-sse-fixed -n glm53-research --type merge -p '{"spec":{"suspend":true}}'` | exit 0 | [logs/infrastructure/20261104T094932.721832Z-prioritize-hicache-pd-stop-standard-sweep](logs/infrastructure/20261104T094932.721832Z-prioritize-hicache-pd-stop-standard-sweep) | User prioritized HiCache and PD; retain completed baseline points and cancel the remaining concurrency-1 run.

- 2026-11-04T09:49:33.908128+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/aggregated-0-fpm-ep1-host32.json` | exit 0 | [logs/infrastructure/20261104T094933.908128Z-hicache32-worker-deploy](logs/infrastructure/20261104T094933.908128Z-hicache32-worker-deploy) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:54:35.652896+00:00 | local | `kubectl --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/aggregated-1-fpm-ep1-host64.json` | exit 0 | [logs/infrastructure/20261104T095435.652896Z-hicache64-worker-deploy](logs/infrastructure/20261104T095435.652896Z-hicache64-worker-deploy) | See captured evidence; no capability inferred from command success alone.

- 2026-11-04T09:59:38Z | both | Started matching HiCache pressure jobs: 128 requests, target 32768/128 tokens, c8, 64 prefix groups with 75% shared prefixes, seed42. Host32 and host64 configurations isolated by Dynamo namespace. Raw outputs in benchmarks/exported/node*/raw/dynamo-ep1-host*/.
- 2026-11-04T10:04:00Z | both | Host32 allocation: 16.87 GiB KV plus15.13 GiB KDA per rank (256 GiB total); Host64:33.74+30.26 GiB per rank (512 GiB total). Host-tier backups and nonzero host-hit counters observed. Performance outcome pending completed-request gate. Initial host64 preflight raced deployment replacement; post-run correctness gate added before PD transition.

- 2026-11-04T10:04:29.940947+00:00 | both | `kubectl --kubeconfig /Users/pkr/glm53-research/.secrets/kubeconfig.yaml -n glm53-research scale deployment aggregated-0 aggregated-1 --replicas=0` | exit 1 | [logs/infrastructure/20261104T100429.940947Z-pd-nixl-transition-0](logs/infrastructure/20261104T100429.940947Z-pd-nixl-transition-0) | Cache benchmarks completed. Starting PD validation; performance and transport remain unverified.

- 2026-11-04T10:05:26.815931+00:00 | both | `kubectl --kubeconfig /Users/pkr/glm53-research/.secrets/kubeconfig.yaml -n glm53-research scale deployment aggregated-0 aggregated-1 --replicas=0` | exit 0 | [logs/infrastructure/20261104T100526.815931Z-pd-nixl-transition-0](logs/infrastructure/20261104T100526.815931Z-pd-nixl-transition-0) | Cache benchmarks completed. Starting PD validation; performance and transport remain unverified.

- 2026-11-04T10:05:31.991285+00:00 | both | `kubectl --request-timeout=45s --kubeconfig .secrets/kubeconfig.yaml -n glm53-research scale deployment aggregated-0 aggregated-1 --replicas=0` | exit 0 | [logs/infrastructure/20261104T100531.991285Z-pd-nixl-transition-retry](logs/infrastructure/20261104T100531.991285Z-pd-nixl-transition-retry) | Both cache request gates passed. Retrying transition after API TLS timeout; PD unverified.

- 2026-11-04T10:05:45.656676+00:00 | both | `kubectl --request-timeout=45s --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/pd-nixl.json -f kubernetes/verify-pd-nixl.json` | exit 0 | [logs/infrastructure/20261104T100545.656676Z-pd-nixl-workers](logs/infrastructure/20261104T100545.656676Z-pd-nixl-workers) | Starting real-weight preview validation; no PD performance claim.
- 2026-11-04T10:05:32Z | both | Cache pressure completed128/128 for host32 and host64. First PD scale attempt partially succeeded due API TLS handshake timeout; retry succeeded. Two transition coordinators overlapped after a process-name termination pattern failed to match the interpreter path; both were stopped and transition completed manually. Host64 post-run semantic validation was interrupted, so it is not accepted as a correctness pass. Added exclusive coordinator lock and explicit API timeouts for future reproduction.

- 2026-11-04T10:11:27.715190+00:00 | both | `kubectl --request-timeout=30s --kubeconfig .secrets/kubeconfig.yaml apply -f kubernetes/bench-pd-nixl-pressure.json` | exit 0 | [logs/infrastructure/20261104T101127.715190Z-pd-nixl-pressure-benchmark](logs/infrastructure/20261104T101127.715190Z-pd-nixl-pressure-benchmark) | Real-weight PD correctness passed arithmetic c1/8/32, prefix retrieval and tools; starting matched pressure benchmark.

- 2026-11-04T10:15:22.167220+00:00 | both | `kubectl --request-timeout=20s --kubeconfig /Users/pkr/glm53-research/.secrets/kubeconfig.yaml -n glm53-research apply -f /Users/pkr/glm53-research/kubernetes/bench-pd-nixl-32k-c32.json` | exit 0 | [logs/infrastructure/20261104T101522.167220Z-bench-pd-nixl-32k-c32](logs/infrastructure/20261104T101522.167220Z-bench-pd-nixl-32k-c32) | Sequential PD comparison; correctness gate required before performance.
- 2026-11-04T10:15:20Z | both | Discovered telemetry samplers exited on unhandled10s nvidia-smi timeout during worker replacement (last samples node0~10:07:01, node1~10:06:19). Raw inference and worker Prometheus logs preserved, but early PD GPU/IB telemetry has a gap. Made sampler resilient to query timeout and restarted both. Summaries now report measurement-window coverage per node; partial-window averages are not complete-run utilization claims.

- 2026-11-04T10:19:17.450810+00:00 | both | `kubectl --request-timeout=20s --kubeconfig /Users/pkr/glm53-research/.secrets/kubeconfig.yaml -n glm53-research apply -f /Users/pkr/glm53-research/kubernetes/pd-nixl-host64.json` | exit 0 | [logs/infrastructure/20261104T101917.450810Z-pd-prefill-host64-transition](logs/infrastructure/20261104T101917.450810Z-pd-prefill-host64-transition) | Sequential PD comparison; correctness gate required before performance.

- 2026-11-04T10:20:57.353947+00:00 | both | `kubectl --request-timeout=20s --kubeconfig /Users/pkr/glm53-research/.secrets/kubeconfig.yaml -n glm53-research apply -f /Users/pkr/glm53-research/kubernetes/bench-pd-nixl-32k-c32.json` | exit 0 | [logs/infrastructure/20261104T102057.353947Z-bench-pd-nixl-32k-c32](logs/infrastructure/20261104T102057.353947Z-bench-pd-nixl-32k-c32) | Sequential PD comparison; correctness gate required before performance.

- 2026-11-04T10:21:03.585391+00:00 | both | `kubectl --request-timeout=20s --kubeconfig /Users/pkr/glm53-research/.secrets/kubeconfig.yaml -n glm53-research apply -f /Users/pkr/glm53-research/kubernetes/pd-nixl-host64.json` | exit 0 | [logs/infrastructure/20261104T102103.585391Z-pd-prefill-host64-transition](logs/infrastructure/20261104T102103.585391Z-pd-prefill-host64-transition) | Sequential PD comparison; correctness gate required before performance.
- 2026-11-04T10:23:00Z | both | NIXL PD c8 andc32 pressure accepted128/128 with104.45 and104.28 output tok/s. Mean TPOT8.31/8.30ms; mean TTFT8.50/33.63s. c32 node0 IB transmit428.83GiB across97.3% measurement-window telemetry coverage. Host64 prefill-only cache now allocating, decode GPU-only. Final capacity test prepared at64K input/256output,128 client concurrency; engine max-running remains32, so admission pressure is distinguished from resident concurrency. Blog companion manifests read and preserved; Qwen4P4D/RoCE topology was not copied to larger GLM/nativeIB.
- 2026-11-04T10:31:22Z | local | Created and verified /Users/pkr/glm53-research-backup-20261104T103122Z.tar.gz:1141 files,14,528,724 bytes,SHA256 b041b667c59c7b8d4bb31a16691296397fa384a84a91c4347d1d4688101b2b78. Completed before user4:08PM IST deadline. Node0 last successful logs export10:29:19UTC; node1 last10:21:43UTC; all accepted benchmarks ended before these exports.
- 2026-11-04T10:33:00Z | both | PD+HiCache startup failed at NIXL UCX backend60s deadline; captured previous container traceback locally. Node1 NotReady/SSH timeout and later node0 SSH timeout blocked further inference/export. No evidence establishes cause. Stopped local benchmark sequence, retained working aggregate/PD manifests and all accepted results. No capacity benchmark128concurrency or64K result claimed. Backup retries continue without provider modifications.
