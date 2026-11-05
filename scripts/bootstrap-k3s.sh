#!/usr/bin/env bash
# Starts only the isolated research cluster; no system installers, reboot,
# provider runtime changes, kernel changes, or operator/driver installation.
set -euo pipefail
root=/root/glm53-research
mkdir -p "$root/bin" "$root/logs/infrastructure" "$root/kubernetes"
test -s "$root/.secrets/cluster.token"
version='v1.34.12+k3s1'
url="https://github.com/k3s-io/k3s/releases/download/${version}"
if ! test -x "$root/bin/k3s"; then
  curl -fL --retry 3 "$url/k3s" -o "$root/bin/k3s"
  curl -fL --retry 3 "$url/sha256sum-amd64.txt" -o "$root/bin/k3s.sha256sums"
  python3 - "$root/bin" <<'PY'
import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1])
expected=[l.split()[0] for l in (p/'k3s.sha256sums').read_text().splitlines() if l.split()[-1] in ['k3s','./k3s']]
assert len(expected)==1
actual=hashlib.sha256((p/'k3s').read_bytes()).hexdigest()
assert actual==expected[0],(actual,expected)
print('k3s SHA256 verified:',actual)
PY
  chmod 755 "$root/bin/k3s"
fi
"$root/bin/k3s" --version
if test -f "$root/k3s.pid" && kill -0 "$(cat "$root/k3s.pid")" 2>/dev/null; then
  echo 'Research k3s process already running'
  exit 0
fi
if ip -4 addr show wg0 | grep -q 10.42.0.1/; then
  role=server
else
  role=agent
fi
test -f "$root/kubernetes/k3s-${role}.yaml"
nohup "$root/bin/k3s" "$role" --config "$root/kubernetes/k3s-${role}.yaml" > "$root/logs/infrastructure/k3s-${role}.log" 2>&1 < /dev/null &
echo "$!" > "$root/k3s.pid"
printf 'Started isolated research k3s %s pid=%s\n' "$role" "$(cat "$root/k3s.pid")"
