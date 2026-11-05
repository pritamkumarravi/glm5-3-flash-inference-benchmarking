#!/usr/bin/env python3
"""Keep every research container log generation before kubelet garbage collection."""
from pathlib import Path
import shutil
import time

source=Path('/var/log/pods')
dest=Path('/root/glm53-research/logs/kubelet')
while True:
    for pod in source.glob('glm53-research_*'):
        for f in pod.glob('*/*.log*'):
            if not f.is_file():continue
            target=dest/f.relative_to(source)
            target.parent.mkdir(parents=True,exist_ok=True)
            try:shutil.copy2(f,target)
            except FileNotFoundError:pass
    time.sleep(20)
