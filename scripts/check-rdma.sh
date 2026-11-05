#!/usr/bin/env bash
# Two bounded host-memory verbs checks. TCP over wg0 exchanges QP metadata;
# data uses native InfiniBand on mlx5_0. This is not a GPU-buffer measurement.
set -u
if ip -4 addr show wg0 | grep -q 10.42.0.1/; then
  role=server
  peer=()
else
  role=client
  peer=(10.42.0.1)
  sleep 3
fi
printf 'timestamp=%s role=%s\n' "$(date -u +%FT%TZ)" "$role"
ib_write_bw --version
printf '\ncommand: ib_write_bw -d mlx5_0 -i 1 -p 18515 -s 8388608 -D 5 --report_gbits %s\n' "${peer[*]}"
timeout 50 ib_write_bw -d mlx5_0 -i 1 -p 18515 -s 8388608 -D 5 --report_gbits "${peer[@]}"
rc=$?
printf 'write_bw_exit=%s\n' "$rc"
if test "$role" = client; then sleep 2; fi
printf '\ncommand: ib_send_lat -d mlx5_0 -i 1 -p 18516 -s 8 -n 10000 %s\n' "${peer[*]}"
timeout 50 ib_send_lat -d mlx5_0 -i 1 -p 18516 -s 8 -n 10000 "${peer[@]}"
lat_rc=$?
printf 'send_lat_exit=%s\n' "$lat_rc"
test "$rc" -eq 0 && test "$lat_rc" -eq 0
