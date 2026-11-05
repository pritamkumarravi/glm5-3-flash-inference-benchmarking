# GLM-5.3-Flash H100 inference research

This directory is the local, non-rental copy of code and evidence for a
two-node, sixteen-H100 experiment. Real FP8 weights and aggregated/PD correctness checks passed. Accepted
measurements and failures are preserved separately. Both rental SSH endpoints
became unreachable during the final PD + HiCache experiment; see the report.

- [Technical report](reports/technical-report.md)
- [Verified backup status](results/backup-status.json)
- [Accepted benchmark data](benchmarks/processed/accepted.csv)
- [Current experiment status](experiment-status.md)
- [Infrastructure evidence](reports/infrastructure-discovery.md)
- [Chronological operations](research-log.md)
- [Experiment status](experiment-status.md)
- `environment/sources/`: immutable upstream snapshots and model metadata.
- `kubernetes/`: isolated research-cluster and workload manifests.
- `scripts/record.py`: timestamped stdout/stderr capture and operation metadata.
- `scripts/export-artifacts.py`: periodic local copying of outputs; credentials
  and model weights are excluded.

Raw logs and upstream snapshots are preserved locally but excluded from Git.
The rentals are scheduled for removal at 10:36 UTC on 2026-11-04. Node-local
model-cache volumes survive pod replacement, not rental termination. No external
Lium volume exists. Keep all experiment outputs in this local directory.

Kubernetes access uses `.secrets/kubeconfig.yaml` and a loopback SSH tunnel on
port 16443. Credentials are excluded from Git and artifact exports.

The FPM reference is TP8/EP1, SGLang 0.5.20, FP8 block weights and BF16 KV.
The current H100 cookbook uses TP8/EP8. These are distinct experimental profiles.
