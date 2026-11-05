#!/usr/bin/env python3
"""Preserve role-specific Prometheus snapshots during PD pressure experiments."""
import datetime as dt
import gzip
from pathlib import Path
import time
import urllib.request

root=Path('/research-logs/worker-metrics')
root.mkdir(parents=True,exist_ok=True)
while True:
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    for role in ['prefill','decode']:
        try:
            data=urllib.request.urlopen(f'http://pd-nixl-{role}:8081/metrics',timeout=10).read()
            with gzip.open(root/f'{stamp}-{role}.prom.gz','wb') as f:f.write(data)
        except Exception as e:
            with (root/'errors.log').open('a') as f:f.write(f'{stamp} {role} {e}\n')
    time.sleep(10)
