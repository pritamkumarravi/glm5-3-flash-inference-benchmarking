#!/usr/bin/env python3
"""Snapshot local research evidence into a verified archive, excluding credentials."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile

root=Path(__file__).resolve().parents[1]
stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
archive=root.parent/f'glm53-research-backup-{stamp}.tar.gz'
with tempfile.TemporaryDirectory(prefix='glm53-artifact-snapshot-') as temporary:
    snapshot=Path(temporary)/'glm53-research';snapshot.mkdir()
    records=[]
    for source in root.rglob('*'):
        rel=source.relative_to(root)
        if any(x in ['.git','.secrets','__pycache__'] for x in rel.parts):continue
        if source.is_symlink() or not source.is_file():continue
        if source.suffix in ['.key','.pem','.token','.pyc'] or source.name.startswith('.env'):continue
        target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
        try:shutil.copy2(source,target)
        except FileNotFoundError:continue
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        records.append(dict(path=str(rel),bytes=target.stat().st_size,sha256=digest))
    manifest=dict(created_utc=stamp,source=str(root),files=records,file_count=len(records),total_bytes=sum(x['bytes'] for x in records),scope='All locally preserved research code, manifests, configs, source snapshots, logs, raw and processed benchmark artifacts; credential files excluded. Remote export failures are recorded in logs/artifact-export.jsonl.')
    (snapshot/'BACKUP-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with tarfile.open(archive,'w:gz') as tar:tar.add(snapshot,arcname='glm53-research')
    with tarfile.open(archive,'r:gz') as tar:
        for row in records:
            data=tar.extractfile('glm53-research/'+row['path']).read()
            assert hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
    archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(archive.suffix+'.sha256').write_text(f'{archive_sha}  {archive.name}\n')
    result=dict(created_utc=stamp,archive=str(archive),sha256=archive_sha,files=len(records),archive_bytes=archive.stat().st_size,verified_all_file_hashes=True)
    (root/'results/backup-status.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
