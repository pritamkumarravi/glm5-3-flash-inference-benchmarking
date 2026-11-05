#!/usr/bin/env python3
"""Capture a non-secret operation locally, with complete stdout and stderr."""
import argparse
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--node', default='local')
    p.add_argument('--label', required=True)
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--configuration', default='read-only discovery')
    p.add_argument('--runtime-version', default='not yet verified')
    p.add_argument('--model-revision', default='not yet verified')
    p.add_argument('--interpretation', default='See captured evidence; no capability inferred from command success alone.')
    p.add_argument('command', nargs=argparse.REMAINDER)
    args = p.parse_args()
    cmd = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not cmd:
        p.error('a command is required after --')
    now = dt.datetime.now(dt.timezone.utc)
    safe_label = ''.join(c if c.isalnum() or c in '-_' else '_' for c in args.label)
    folder = ROOT / 'logs/infrastructure' / (now.strftime('%Y%m%dT%H%M%S.%fZ') + '-' + safe_label)
    folder.mkdir(parents=True)
    start = time.monotonic()
    with (folder/'stdout.txt').open('w') as out, (folder/'stderr.txt').open('w') as err:
        try:
            result = subprocess.run(cmd, stdout=out, stderr=err, timeout=args.timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
            err.write(f'\nLocal timeout after {args.timeout}s\n')
        except OSError as exc:
            code = 127
            err.write(str(exc)+'\n')
    record = dict(timestamp=now.isoformat(), node=args.node, command=shlex.join(cmd),
                  configuration=args.configuration, runtime_version=args.runtime_version,
                  model_revision=args.model_revision, exit_code=code,
                  elapsed_seconds=round(time.monotonic()-start, 3),
                  outcome='success' if code == 0 else 'failed', artifact=str(folder.relative_to(ROOT)),
                  interpretation=args.interpretation)
    (folder/'metadata.json').write_text(json.dumps(record, indent=2)+'\n')
    with (ROOT/'environment/operations.jsonl').open('a') as f:
        f.write(json.dumps(record)+'\n')
    with (ROOT/'research-log.md').open('a') as f:
        f.write(f"\n- {record['timestamp']} | {args.node} | `{shlex.join(cmd)}` | exit {code} | "
                f"[{record['artifact']}]({record['artifact']}) | {args.interpretation}\n")
    print(json.dumps(record, indent=2))
    sys.exit(code)

if __name__ == '__main__':
    main()
