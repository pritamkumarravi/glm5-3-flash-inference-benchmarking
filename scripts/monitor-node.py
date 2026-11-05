#!/usr/bin/env python3
"""Sample GPU, network, host-memory and InfiniBand counters without GPU work."""
import datetime as dt
import json
from pathlib import Path
import socket
import subprocess
import time

out=Path('/root/glm53-research/logs/infrastructure')
out.mkdir(parents=True,exist_ok=True)
gpu_fields='index,uuid,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw,temperature.gpu,clocks.sm,clocks.mem'
with (out/'telemetry.jsonl').open('a',buffering=1) as f:
    while True:
        row={'timestamp':dt.datetime.now(dt.timezone.utc).isoformat(),'node':socket.gethostname()}
        row['gpu_fields']=gpu_fields.split(',')
        try:
            p=subprocess.run(['nvidia-smi','--query-gpu='+gpu_fields,'--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=10)
            row['gpu_csv']=p.stdout.splitlines()
            if p.returncode:row['gpu_error']=p.stderr
        except (subprocess.TimeoutExpired,OSError) as e:
            row['gpu_error']=str(e)
            row['gpu_csv']=[]
        row['meminfo']={k:v.strip() for l in Path('/proc/meminfo').read_text().splitlines() for k,v in [l.split(':',1)]}
        row['net_dev']=Path('/proc/net/dev').read_text()
        row['ib_counters']={}
        for p in Path('/sys/class/infiniband').glob('*/ports/*/counters/*'):
            if p.name in ['port_xmit_data','port_rcv_data','port_xmit_packets','port_rcv_packets','port_xmit_wait','port_rcv_errors','port_xmit_discards']:
                try:row['ib_counters'][str(p)]=int(p.read_text().strip())
                except (OSError,ValueError):pass
        for n in ['memory.current','memory.peak','memory.events']:
            p=Path('/sys/fs/cgroup')/n
            if p.exists():row[n]=p.read_text().strip()
        f.write(json.dumps(row)+'\n')
        time.sleep(2)
