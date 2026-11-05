#!/usr/bin/env python3
"""Summarize accepted measurements and align device telemetry to timed windows."""
import csv
import datetime as dt
import json
from pathlib import Path
import re
import statistics

ROOT=Path(__file__).resolve().parents[1]

def metrics(path):
    result={}
    if not path.exists():return result
    for line in path.read_text().splitlines():
        if line.startswith('#'):continue
        m=re.match(r'([^\s{]+)(?:\{(.*)\})?\s+([^\s]+)',line)
        if not m:continue
        name,labels,value=m.groups()
        labels=dict(re.findall(r'(\w+)="([^"]*)"',labels or ''))
        if 'tp_rank' in labels and labels['tp_rank']!='0':continue
        if name=='sglang:prefill_effective_tokens_total':key=labels.get('mode')+'_tokens'
        elif name in ['sglang:hicache_backup_bytes_total','sglang:hicache_load_bytes_total','sglang:hicache_host_total_tokens','sglang:hicache_host_used_tokens']:key=name.split(':')[1]
        elif name in ['sglang:hicache_backup_tokens_total','sglang:hicache_load_tokens_total','sglang:hicache_dropped_tokens_total']:key=name.split(':')[1]+'_'+labels.get('pool','')+'_'+labels.get('reason','')
        else:continue
        result[key]=result.get(key,0)+float(value)
    return result

telemetry={}
for node in ['node0','node1']:
    p=ROOT/f'logs/exported/{node}/infrastructure/telemetry.jsonl'
    rows=[]
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                row=json.loads(line); row['epoch']=dt.datetime.fromisoformat(row['timestamp']).timestamp(); rows.append(row)
            except (ValueError,KeyError):pass
    telemetry[node]=rows

accepted=[];failed=[]
for path in sorted((ROOT/'benchmarks/exported').glob('*/raw/*/*/metadata.json')):
    try:m=json.loads(path.read_text())
    except ValueError:continue
    base=dict(profile=m['profile'],suite=m['suite'],concurrency=m['concurrency'],repetition=m['repetition'],artifact=str(path.parent.relative_to(ROOT)))
    if not m.get('request_gate_passed') or m.get('exit_code')!=0:
        failed.append(base|dict(exit_code=m.get('exit_code'),completed=m.get('completed'),output_gate=m.get('output_length_gate_passed')));continue
    result=json.loads(path.with_name('result.jsonl').read_text().splitlines()[-1])
    row=base|{k:result.get(k) for k in ['duration','completed','total_input_tokens','total_output_tokens','request_throughput','input_throughput','output_throughput','total_throughput','mean_ttft_ms','median_ttft_ms','p90_ttft_ms','p95_ttft_ms','p99_ttft_ms','mean_tpot_ms','p95_tpot_ms','mean_itl_ms','p95_itl_ms']}
    row.update(input_target=m['input_target'],output_target=m['output_target'],prefix_fraction=m['shared_prefix_fraction'],allocated_gpus=m.get('allocated_gpus',8),model_revision=m['model_revision'])
    row['output_tokens_per_gpu_s']=row['output_throughput']/row['allocated_gpus']
    before=metrics(path.with_name('metrics-before.txt'));after=metrics(path.with_name('metrics-after.txt'))
    row['cache_counter_delta_including_warmup']={k:v-before.get(k,0) for k,v in after.items() if 'total_tokens' not in k and 'used_tokens' not in k}
    row['cache_capacity_after']={k:v for k,v in after.items() if 'total_tokens' in k or 'used_tokens' in k}
    try:
        window=json.loads(path.with_name('measurement-window.json').read_text())
        start=next(x['wall_time'] for x in window if x['stage']=='start');end=next(x['wall_time'] for x in window if x['stage']=='end')
        node=path.relative_to(ROOT/'benchmarks/exported').parts[0]
        nodes=['node0','node1'] if row['allocated_gpus']==16 else [node]
        row['telemetry_by_node']={}
        for selected_node in nodes:
            node_samples=[x for x in telemetry[selected_node] if start<=x['epoch']<=end]
            gpu_rows=[list(map(float,[v.strip() for v in l.split(',')][2:])) for x in node_samples for l in x.get('gpu_csv',[])]
            if gpu_rows:
                ib_first=node_samples[0].get('ib_counters',{});ib_last=node_samples[-1].get('ib_counters',{})
                row['telemetry_by_node'][selected_node]=dict(samples=len(node_samples),mean_gpu_util_percent=statistics.mean(x[0] for x in gpu_rows),mean_gpu_power_w=statistics.mean(x[4] for x in gpu_rows),peak_vram_mib=max(x[2] for x in gpu_rows),ib_xmit_bytes=sum(max(0,v-ib_first.get(k,v))*4 for k,v in ib_last.items() if k.endswith('/port_xmit_data')),ib_rcv_bytes=sum(max(0,v-ib_first.get(k,v))*4 for k,v in ib_last.items() if k.endswith('/port_rcv_data')))
                gaps=[b['epoch']-a['epoch'] for a,b in zip(node_samples,node_samples[1:])]
                row['telemetry_by_node'][selected_node]['approximate_window_coverage_fraction']=sum(min(5,x) for x in gaps)/(end-start)
                row['telemetry_by_node'][selected_node]['largest_sample_gap_seconds']=max(gaps,default=end-start)
        samples=[x for n in nodes for x in telemetry[n] if start<=x['epoch']<=end]
        values=[list(map(float,[v.strip() for v in l.split(',')][2:])) for x in samples for l in x.get('gpu_csv',[])]
        if values:
            row['telemetry']=dict(samples=len(samples),gpu_mean_util_percent=statistics.mean(x[0] for x in values),gpu_mean_memory_util_percent=statistics.mean(x[1] for x in values),gpu_mean_vram_mib=statistics.mean(x[2] for x in values),gpu_peak_vram_mib=max(x[2] for x in values),gpu_mean_power_w=statistics.mean(x[4] for x in values),gpu_peak_temperature_c=max(x[5] for x in values),max_node_cgroup_gib=max(int(x.get('memory.current','0'))/2**30 for x in samples))
    except (OSError,ValueError,StopIteration,KeyError):pass
    accepted.append(row)

out=ROOT/'benchmarks/processed';out.mkdir(parents=True,exist_ok=True)
(out/'accepted.json').write_text(json.dumps(accepted,indent=2)+'\n')
(out/'failed.json').write_text(json.dumps(failed,indent=2)+'\n')
if accepted:
    keys=[k for k in accepted[0] if k not in ['telemetry','telemetry_by_node','cache_counter_delta_including_warmup','cache_capacity_after']]
    with (out/'accepted.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(accepted)
print(json.dumps([dict(profile=x['profile'],suite=x['suite'],c=x['concurrency'],output_tps=round(x['output_throughput'],2),mean_ttft_ms=round(x['mean_ttft_ms'],2),cache=x.get('cache_counter_delta_including_warmup'),telemetry=x.get('telemetry')) for x in accepted],indent=2))
