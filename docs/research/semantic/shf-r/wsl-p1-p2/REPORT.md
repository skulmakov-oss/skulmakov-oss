# SHF-R — WSL Ubuntu VM Performance: Baseline vs P1 vs P2


## Executive result

P1 removes the measured Map construction bottleneck; P2 removes the measured Record+Sequence bottleneck. These gains come with reproduced constant-factor regressions in several existing linear workloads. Calls=16384 remains a hard blocker. Recommend P3 contract work next; no implementation has begun.

Primary results: 558 runs including controls; additional confirmation: 168 runs. Separate compile/verify: 1104 successful commands; O0/O1: 24 successful pure parity pairs, six unsupported filesystem pairs. Full distinctions, failures, hashes and limitations follow.

## A. Environment and provenance

Actual Ubuntu-24.04 WSL2, native ext4. No source patches or dependency installation. See environment-builds.json, input-hashes.json, artifact-hashes.json and METHODOLOGY.md for full provenance.

BASELINE `94c5c50d16c3f2efc7691456755461bedae83b18`; P1 `758738a2edf0e984d6067fb372f003a381723d02`; P2 `188dec7eddfafaab5926af2d30f528bfe3d89a2c`.


### Exact host and builds

```text
PRETTY_NAME="Ubuntu 24.04.5 LTS"
Linux ARCHIVE_HOST 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
rustc 1.97.1 (8bab26f4f 2026-07-14)
binary: rustc
commit-hash: 8bab26f4f68e0e26f0bb7960be334d5b520ea452
commit-date: 2026-07-14
host: x86_64-unknown-linux-gnu
release: 1.97.1
LLVM version: 22.1.6
cargo 1.97.1 (c980f4866 2026-06-30)
gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
git version 2.43.0
Architecture:                         x86_64
CPU(s):                               8
Model name:                           Intel(R) Core(TM) i5-9300H CPU @ 2.40GHz
Thread(s) per core:                   2
Core(s) per socket:                   4
total        used        free      shared  buff/cache   available
Mem:     10364145664   617709568  9556955136     3289088   438714368  9746436096
Swap:     3221225472           0  3221225472
Filesystem     Type  1K-blocks     Used Available Use% Mounted on
/dev/sdc       ext4 1055762868 40981752 961077644   5% /
	libopenblas.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libopenblas.so.0
	libopenblas.so (libc6,x86-64) => /lib/x86_64-linux-gnu/libopenblas.so
```

WSL runtime version:

```text
5@A8O WSL: 2.4.10.0

5@A8O O4@0: 5.15.167.4-1

5@A8O WSLg: 1.0.65

5@A8O MSRDC: 1.2.5716

5@A8O Direct3D: 1.611.1-81528511

5@A8O DXCore: 10.0.26100.1-240331-1435.ge-release

5@A8O Windows: 10.0.26340.9616
```

Build settings: `opt-level=3`, `lto=true`, `codegen-units=1`, `panic=abort`, `strip=symbols`; `CARGO_BUILD_JOBS=2`. Execution thread env: `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`.

|Revision|Source SHA|Cargo.lock SHA-256|Binary SHA-256|
|---|---|---|---|
|baseline|`94c5c50d16c3f2efc7691456755461bedae83b18`|`5d85791ca1194f6fc6142ed96b1d3bf5ca0f4b05104689f824f364f7a4e6c0d8`|`efac7456ce51feb24f5ac3ef6e2c5b881552b9227171031ca5f73fab50458485`|
|p1|`758738a2edf0e984d6067fb372f003a381723d02`|`5d85791ca1194f6fc6142ed96b1d3bf5ca0f4b05104689f824f364f7a4e6c0d8`|`85ee369857fb8a67d9c0320069c3a5ab8c56917ce7fb6d1467c1b8559838412a`|
|p2|`188dec7eddfafaab5926af2d30f528bfe3d89a2c`|`5d85791ca1194f6fc6142ed96b1d3bf5ca0f4b05104689f824f364f7a4e6c0d8`|`68459dc0778f78700d245352b4cde5cb4d26f8e5a5ad6947bb16d591d9c1a941`|

Compiler binary SHA-256: `d3a664c970a9fd8361b64194861bebc1ae37b9054e5ee3400dc1c9e691797eea`.

Build command for each detached checkout: `CARGO_NET_OFFLINE=true CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=<separate target> cargo build --release -p smc-cli --locked --offline`. All builds exit 0.

Execution template: `target-<revision>/release/smc-cli run workloads/<family>_<N>.sm --profile <pure|cli-read-only> --root workloads/root --envelope trusted-compiler --max-steps 200000000 --metrics json`. Text and lex use cli-read-only; remaining cases use pure. Warm-up trial -1 excluded from statistics; measured order rotates B/P1/P2, P1/P2/B, P2/B/P1. Timeout 120 seconds per invocation.

OpenBLAS package metadata / Linux contention snapshot:

```text
{
  "dpkg-query -W libopenblas0-pthread libopenblas-dev": {
    "exit": 0,
    "output": "libopenblas-dev:amd64\t0.3.26+ds-1ubuntu0.1\nlibopenblas0-pthread:amd64\t0.3.26+ds-1ubuntu0.1\n"
  },
  "ps -eo pid,comm,pcpu,pmem": {
    "exit": 0,
    "output": "your 131072x1 screen size is bogus. expect trouble\n    PID COMMAND         %CPU %MEM\n      1 systemd          0.1  0.1\n      2 init-systemd(Ub  0.0  0.0\n      7 init             0.0  0.0\n     51 systemd-journal  0.0  0.1\n    101 systemd-udevd    0.0  0.0\n    108 systemd-resolve  0.0  0.1\n    109 systemd-timesyn  0.0  0.0\n    158 cron             0.0  0.0\n    159 dbus-daemon      0.0  0.0\n    169 systemd-logind   0.0  0.0\n    186 agetty           0.0  0.0\n    190 rsyslogd         0.0  0.0\n    200 agetty           0.0  0.0\n    217 unattended-upgr  0.0  0.2\n    302 login            0.0  0.0\n    346 systemd          0.0  0.1\n    347 (sd-pam)         0.0  0.0\n    358 bash             0.0  0.0\n   2479 polkitd          0.0  0.0\n   6244 SessionLeader    0.0  0.0\n   6245 Relay(6252)      0.0  0.0\n   6252 python3          0.0  0.1\n   6277 python3          0.0  0.2\n   6669 wsl-pro-service  0.1  0.1\n   7046 packagekitd      0.3  0.2\n   7181 time             0.0  0.0\n   7183 smc-cli          109  0.1\n   7192 SessionLeader    0.0  0.0\n   7193 Relay(7200)      0.0  0.0\n   7194 (udev-worker)    0.0  0.0\n   7195 (udev-worker)    0.0  0.0\n   7196 (udev-worker)    0.0  0.0\n   7197 (udev-worker)    0.0  0.0\n   7198 (udev-worker)    0.0  0.0\n   7199 (udev-worker)    0.0  0.0\n   7200 python3         37.0  0.1\n   7202 ps               0.0  0.0\n"
  },
  "cat /proc/loadavg": {
    "exit": 0,
    "output": "1.24 1.09 1.10 2/216 7203\n"
  }
}
```

## B. End-to-end CLI comparison

Times are milliseconds, external wall clock; three measured samples after warm-up. Success requires exit 0 plus metrics outcome ok (self-asserting sources). No failed sample is used for speedup.

|Workload|N|Baseline ms [range]|P1 ms [range]|P2 ms [range]|B/P2|B/P1|P1/P2|Outcome|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|lex_calls|1000|13.69 [12.37–21.30]|15.23 [12.54–15.51]|18.67 [16.75–19.89]|0.73x|0.90x|0.82x|ok / ok / ok|
|lex_calls|4000|41.58 [34.47–55.70]|34.56 [31.39–35.36]|47.88 [40.88–59.75]|0.87x|1.20x|0.72x|ok / ok / ok|
|lex_calls|16000|157.08 [134.51–172.71]|143.72 [130.16–145.63]|173.24 [163.28–201.10]|0.91x|1.09x|0.83x|ok / ok / ok|
|lex_calls|32000|quota_exceeded|quota_exceeded|quota_exceeded|—|—|—|quota_exceeded / quota_exceeded / quota_exceeded|
|map_get|1000|170.50 [154.59–173.11]|14.44 [12.76–18.46]|16.05 [15.49–17.71]|10.62x|11.80x|0.90x|ok / ok / ok|
|map_get|4000|2488.95 [2470.77–2655.87]|35.35 [34.86–35.90]|46.43 [45.67–48.90]|53.61x|70.40x|0.76x|ok / ok / ok|
|map_get|16000|54637.87 [45392.68–76697.07]|148.58 [131.34–154.80]|180.89 [167.99–184.88]|302.05x|367.74x|0.82x|ok / ok / ok|
|map_get|32000|TIMEOUT|250.22 [246.46–280.50]|357.88 [356.15–491.50]|—|—|0.70x|TIMEOUT / ok / ok|
|map_set|1000|122.74 [114.71–189.50]|17.83 [15.30–22.11]|19.28 [18.43–34.31]|6.37x|6.88x|0.92x|ok / ok / ok|
|map_set|4000|2870.08 [1292.29–2926.61]|51.72 [20.11–52.95]|55.73 [26.40–65.50]|51.50x|55.50x|0.93x|ok / ok / ok|
|map_set|16000|34965.47 [27975.94–38002.88]|66.74 [64.23–70.11]|81.68 [79.78–86.00]|428.06x|523.91x|0.82x|ok / ok / ok|
|map_set|32000|85752.31 [81239.91–86444.71]|130.90 [127.82–146.32]|159.01 [156.05–161.32]|539.28x|655.10x|0.82x|ok / ok / ok|
|map_versions|1000|178.48 [178.40–222.52]|13.45 [12.70–14.80]|17.43 [16.65–21.04]|10.24x|13.27x|0.77x|ok / ok / ok|
|map_versions|4000|2739.87 [2702.64–3138.43]|35.13 [34.74–35.16]|41.77 [28.72–47.08]|65.60x|77.99x|0.84x|ok / ok / ok|
|map_versions|16000|68634.48 [67055.60–69365.12]|145.35 [128.91–148.82]|161.56 [157.41–183.15]|424.83x|472.22x|0.90x|ok / ok / ok|
|map_versions|32000|TIMEOUT|298.37 [297.74–300.11]|423.12 [349.90–469.45]|—|—|0.71x|TIMEOUT / ok / ok|
|record_with|1000|12.25 [11.71–13.65]|12.73 [12.03–15.92]|19.01 [14.26–22.15]|0.64x|0.96x|0.67x|ok / ok / ok|
|record_with|4000|29.03 [23.39–33.83]|35.76 [25.20–39.45]|42.73 [42.08–56.87]|0.68x|0.81x|0.84x|ok / ok / ok|
|record_with|16000|82.88 [77.84–109.98]|81.96 [79.34–83.52]|147.46 [119.06–154.96]|0.56x|1.01x|0.56x|ok / ok / ok|
|record_with|32000|179.79 [147.44–180.24]|177.72 [169.65–180.68]|296.33 [294.40–320.89]|0.61x|1.01x|0.60x|ok / ok / ok|
|seq_push|1000|9.44 [8.73–9.56]|9.59 [8.79–10.84]|9.36 [9.31–11.77]|1.01x|0.98x|1.02x|ok / ok / ok|
|seq_push|4000|17.84 [16.10–20.76]|19.95 [16.04–20.42]|20.47 [18.60–23.49]|0.87x|0.89x|0.97x|ok / ok / ok|
|seq_push|16000|50.43 [47.75–54.79]|45.59 [42.35–59.26]|65.27 [63.44–97.91]|0.77x|1.11x|0.70x|ok / ok / ok|
|seq_push|32000|90.18 [87.95–102.11]|92.48 [73.10–117.67]|111.55 [102.93–112.86]|0.81x|0.98x|0.83x|ok / ok / ok|
|seq_read|1000|12.20 [11.63–17.47]|13.98 [11.93–15.76]|17.08 [14.86–20.26]|0.71x|0.87x|0.82x|ok / ok / ok|
|seq_read|4000|27.95 [24.13–30.38]|25.05 [23.99–28.59]|36.37 [31.36–36.59]|0.77x|1.12x|0.69x|ok / ok / ok|
|seq_read|16000|101.93 [94.07–102.64]|94.41 [94.11–94.98]|134.28 [121.77–144.22]|0.76x|1.08x|0.70x|ok / ok / ok|
|seq_read|32000|160.52 [152.64–184.14]|159.01 [156.55–164.33]|230.28 [219.30–289.68]|0.70x|1.01x|0.69x|ok / ok / ok|
|state10|8000|1834.20 [1671.54–1835.10]|1587.31 [1578.20–2062.68]|130.74 [109.43–131.66]|14.03x|1.16x|12.14x|ok / ok / ok|
|state10|16000|7371.63 [7174.31–7518.01]|7934.26 [7373.64–8206.98]|240.03 [196.17–264.88]|30.71x|0.93x|33.05x|ok / ok / ok|
|state10|32000|28172.92 [26470.55–29520.80]|27815.31 [24946.66–29438.82]|427.03 [381.81–503.08]|65.97x|1.01x|65.14x|ok / ok / ok|
|state5|8000|1697.85 [1530.49–1709.19]|1686.06 [1587.12–1888.73]|84.48 [79.60–109.80]|20.10x|1.01x|19.96x|ok / ok / ok|
|state5|16000|6835.27 [6409.60–6929.76]|7122.70 [5437.52–7319.21]|137.16 [129.59–183.44]|49.84x|0.96x|51.93x|ok / ok / ok|
|state5|32000|27744.32 [23781.11–28572.77]|26916.90 [26088.86–28694.91]|269.05 [193.13–271.22]|103.12x|1.03x|100.04x|ok / ok / ok|
|state_record_map|1000|514.95 [502.77–554.71]|12.80 [12.06–13.66]|14.77 [14.58–16.57]|34.87x|40.22x|0.87x|ok / ok / ok|
|state_record_map|4000|9359.33 [9336.38–9414.45]|33.24 [32.63–33.67]|40.69 [40.11–47.13]|230.00x|281.56x|0.82x|ok / ok / ok|
|state_record_map|16000|TIMEOUT|114.22 [114.07–115.83]|154.24 [152.79–155.06]|—|—|0.74x|TIMEOUT / ok / ok|
|state_record_map|32000|TIMEOUT|247.52 [238.84–256.03]|324.55 [315.27–393.32]|—|—|0.76x|TIMEOUT / ok / ok|
|state_record_seq|1000|30.88 [26.99–33.33]|27.86 [27.83–34.34]|13.70 [12.43–14.50]|2.25x|1.11x|2.03x|ok / ok / ok|
|state_record_seq|4000|262.10 [232.55–268.99]|261.94 [245.85–296.52]|18.56 [17.67–23.86]|14.12x|1.00x|14.12x|ok / ok / ok|
|state_record_seq|16000|7171.10 [6840.10–8569.56]|6965.57 [6936.92–7083.03]|104.48 [100.68–122.35]|68.64x|1.03x|66.67x|ok / ok / ok|
|state_record_seq|32000|27026.57 [24099.54–28044.23]|25150.68 [22882.90–28711.79]|186.38 [185.67–195.22]|145.00x|1.07x|134.94x|ok / ok / ok|
|text_scan|1000|10.72 [9.88–11.62]|11.05 [9.94–11.28]|12.66 [11.52–14.20]|0.85x|0.97x|0.87x|ok / ok / ok|
|text_scan|4000|22.03 [21.37–27.21]|23.34 [22.64–24.73]|29.96 [27.90–32.83]|0.74x|0.94x|0.78x|ok / ok / ok|
|text_scan|16000|88.23 [85.11–105.31]|95.50 [85.27–108.29]|134.89 [134.34–135.26]|0.65x|0.92x|0.71x|ok / ok / ok|
|text_scan|32000|216.80 [212.99–236.08]|211.30 [199.03–257.08]|278.44 [276.50–305.97]|0.78x|1.03x|0.76x|ok / ok / ok|

## C. Scaling

OLS slope log(T) vs log(N), successful medians only. Startup and noise affect small cases. Range of adjacent slopes is descriptive, not a confidence interval.

|Workload|Baseline p|P1 p|P2 p|
|---|---:|---:|---:|
|lex_calls|0.88 (adj 0.80..0.96; 3 pts)|0.81 (adj 0.59..1.03; 3 pts)|0.80 (adj 0.68..0.93; 3 pts)|
|map_get|2.08 (adj 1.93..2.23; 3 pts)|0.85 (adj 0.65..1.04; 4 pts)|0.90 (adj 0.77..0.98; 4 pts)|
|map_set|1.90 (adj 1.29..2.27; 4 pts)|0.52 (adj 0.18..0.97; 4 pts)|0.56 (adj 0.28..0.96; 4 pts)|
|map_versions|2.15 (adj 1.97..2.32; 3 pts)|0.90 (adj 0.69..1.04; 4 pts)|0.91 (adj 0.63..1.39; 4 pts)|
|record_with|0.76 (adj 0.62..1.12; 4 pts)|0.73 (adj 0.60..1.12; 4 pts)|0.80 (adj 0.58..1.01; 4 pts)|
|seq_push|0.65 (adj 0.46..0.84; 4 pts)|0.64 (adj 0.53..1.02; 4 pts)|0.73 (adj 0.56..0.84; 4 pts)|
|seq_read|0.77 (adj 0.60..0.93; 4 pts)|0.73 (adj 0.42..0.96; 4 pts)|0.77 (adj 0.55..0.94; 4 pts)|
|state10|1.97 (adj 1.93..2.01; 3 pts)|2.07 (adj 1.81..2.32; 3 pts)|0.85 (adj 0.83..0.88; 3 pts)|
|state5|2.02 (adj 2.01..2.02; 3 pts)|2.00 (adj 1.92..2.08; 3 pts)|0.84 (adj 0.70..0.97; 3 pts)|
|state_record_map|INCONCLUSIVE (<3 successful sizes)|0.85 (adj 0.69..1.12; 4 pts)|0.89 (adj 0.73..1.07; 4 pts)|
|state_record_seq|2.00 (adj 1.54..2.39; 4 pts)|2.01 (adj 1.62..2.37; 4 pts)|0.80 (adj 0.22..1.25; 4 pts)|
|text_scan|0.87 (adj 0.52..1.30; 4 pts)|0.86 (adj 0.54..1.15; 4 pts)|0.91 (adj 0.62..1.09; 4 pts)|

## D. Determinism and correctness

|Workload|N|Within-revision counters stable|Across-revision counters equal|Outcomes equal|
|---|---:|---|---|---|
|lex_calls|1000|PASS|PASS|PASS|
|lex_calls|4000|PASS|PASS|PASS|
|lex_calls|16000|PASS|PASS|PASS|
|lex_calls|32000|PASS|PASS|PASS|
|map_get|1000|PASS|PASS|PASS|
|map_get|4000|PASS|PASS|PASS|
|map_get|16000|PASS|PASS|PASS|
|map_get|32000|NOT MEASURED (timeout/no execution)|NOT COMPARABLE|NOT COMPARABLE (timeout)|
|map_set|1000|PASS|PASS|PASS|
|map_set|4000|PASS|PASS|PASS|
|map_set|16000|PASS|PASS|PASS|
|map_set|32000|PASS|PASS|PASS|
|map_versions|1000|PASS|PASS|PASS|
|map_versions|4000|PASS|PASS|PASS|
|map_versions|16000|PASS|PASS|PASS|
|map_versions|32000|NOT MEASURED (timeout/no execution)|NOT COMPARABLE|NOT COMPARABLE (timeout)|
|record_with|1000|PASS|PASS|PASS|
|record_with|4000|PASS|PASS|PASS|
|record_with|16000|PASS|PASS|PASS|
|record_with|32000|PASS|PASS|PASS|
|seq_push|1000|PASS|PASS|PASS|
|seq_push|4000|PASS|PASS|PASS|
|seq_push|16000|PASS|PASS|PASS|
|seq_push|32000|PASS|PASS|PASS|
|seq_read|1000|PASS|PASS|PASS|
|seq_read|4000|PASS|PASS|PASS|
|seq_read|16000|PASS|PASS|PASS|
|seq_read|32000|PASS|PASS|PASS|
|state10|8000|PASS|PASS|PASS|
|state10|16000|PASS|PASS|PASS|
|state10|32000|PASS|PASS|PASS|
|state5|8000|PASS|PASS|PASS|
|state5|16000|PASS|PASS|PASS|
|state5|32000|PASS|PASS|PASS|
|state_record_map|1000|PASS|PASS|PASS|
|state_record_map|4000|PASS|PASS|PASS|
|state_record_map|16000|NOT MEASURED (timeout/no execution)|NOT COMPARABLE|NOT COMPARABLE (timeout)|
|state_record_map|32000|NOT MEASURED (timeout/no execution)|NOT COMPARABLE|NOT COMPARABLE (timeout)|
|state_record_seq|1000|PASS|PASS|PASS|
|state_record_seq|4000|PASS|PASS|PASS|
|state_record_seq|16000|PASS|PASS|PASS|
|state_record_seq|32000|PASS|PASS|PASS|
|text_scan|1000|PASS|PASS|PASS|
|text_scan|4000|PASS|PASS|PASS|
|text_scan|16000|PASS|PASS|PASS|
|text_scan|32000|PASS|PASS|PASS|

## E. Resources, failures and unsupported measurements

Full quotas/counters/error classes and RSS are preserved in measurements.jsonl. Peak RSS includes compilation+verification+execution inside the CLI process. Aggregate allocations, VM-only execution time and isolated planner time: NOT MEASURED.

### Every non-successful measured run / negative control

- run map_get N=32000 baseline trial=0: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run map_get N=32000 baseline trial=1: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run map_get N=32000 baseline trial=2: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run map_versions N=32000 baseline trial=0: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run map_versions N=32000 baseline trial=1: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run map_versions N=32000 baseline trial=2: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run state_record_map N=16000 baseline trial=0: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run state_record_map N=16000 baseline trial=1: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run state_record_map N=16000 baseline trial=2: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run state_record_map N=32000 baseline trial=0: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run state_record_map N=32000 baseline trial=1: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run state_record_map N=32000 baseline trial=2: exit=-9, timeout=True, outcome=None, counters=None, quota=None; error=None
- run lex_calls N=32000 baseline trial=0: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 p1 trial=0: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 p2 trial=0: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 p1 trial=1: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 p2 trial=1: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 baseline trial=1: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 p2 trial=2: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 baseline trial=2: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- run lex_calls N=32000 p1 trial=2: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 559809, 'calls': 16384, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Calls', 'limit': 16384, 'used': 16385}; error=quota exceeded: Calls limit=16384 used=16385
- calls-default-steps lex_calls N=32000 baseline trial=0: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 100000, 'calls': 2926, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Steps', 'limit': 100000, 'used': 100001}; error=quota exceeded: Steps limit=100000 used=100001
- capability-denial text_scan N=1000 baseline trial=0: exit=1, timeout=False, outcome=capability_denied, counters={'steps': 2, 'calls': 0, 'peak_frames': 1, 'effect_calls': 0}, quota=None; error=capability FsRead denied for FsRead [prom.cap.manifest v1 MissingCapability]: manifest does not grant this capability
- calls-default-steps lex_calls N=32000 p1 trial=0: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 100000, 'calls': 2926, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Steps', 'limit': 100000, 'used': 100001}; error=quota exceeded: Steps limit=100000 used=100001
- capability-denial text_scan N=1000 p1 trial=0: exit=1, timeout=False, outcome=capability_denied, counters={'steps': 2, 'calls': 0, 'peak_frames': 1, 'effect_calls': 0}, quota=None; error=capability FsRead denied for FsRead [prom.cap.manifest v1 MissingCapability]: manifest does not grant this capability
- calls-default-steps lex_calls N=32000 p2 trial=0: exit=1, timeout=False, outcome=quota_exceeded, counters={'steps': 100000, 'calls': 2926, 'peak_frames': 2, 'effect_calls': 1}, quota={'kind': 'Steps', 'limit': 100000, 'used': 100001}; error=quota exceeded: Steps limit=100000 used=100001
- capability-denial text_scan N=1000 p2 trial=0: exit=1, timeout=False, outcome=capability_denied, counters={'steps': 2, 'calls': 0, 'peak_frames': 1, 'effect_calls': 0}, quota=None; error=capability FsRead denied for FsRead [prom.cap.manifest v1 MissingCapability]: manifest does not grant this capability

### Separate CLI compilation and verification

Standalone compile/verify times include command overhead; they are not isolated application-run phases.

|Source|Revision|Compile median ms|Verify median ms|
|---|---|---:|---:|
|lex_calls_1000.sm|baseline|11.185|4.768|
|lex_calls_1000.sm|p1|12.091|5.582|
|lex_calls_1000.sm|p2|12.253|5.959|
|lex_calls_16000.sm|baseline|14.969|5.596|
|lex_calls_16000.sm|p1|14.492|5.682|
|lex_calls_16000.sm|p2|12.916|5.504|
|lex_calls_32000.sm|baseline|11.361|6.090|
|lex_calls_32000.sm|p1|15.194|5.470|
|lex_calls_32000.sm|p2|12.566|5.190|
|lex_calls_4000.sm|baseline|13.413|5.369|
|lex_calls_4000.sm|p1|11.988|5.210|
|lex_calls_4000.sm|p2|11.837|5.018|
|map_get_1000.sm|baseline|12.745|5.547|
|map_get_1000.sm|p1|13.875|5.523|
|map_get_1000.sm|p2|14.231|5.117|
|map_get_16000.sm|baseline|12.701|5.953|
|map_get_16000.sm|p1|11.983|4.836|
|map_get_16000.sm|p2|12.000|6.041|
|map_get_32000.sm|baseline|12.430|5.277|
|map_get_32000.sm|p1|12.537|5.897|
|map_get_32000.sm|p2|12.194|5.464|
|map_get_4000.sm|baseline|12.809|4.999|
|map_get_4000.sm|p1|13.667|4.832|
|map_get_4000.sm|p2|12.160|5.487|
|map_set_1000.sm|baseline|13.545|5.998|
|map_set_1000.sm|p1|12.210|5.759|
|map_set_1000.sm|p2|13.503|6.437|
|map_set_16000.sm|baseline|12.515|4.987|
|map_set_16000.sm|p1|13.721|6.061|
|map_set_16000.sm|p2|12.969|5.967|
|map_set_32000.sm|baseline|12.356|5.412|
|map_set_32000.sm|p1|12.584|5.168|
|map_set_32000.sm|p2|13.662|5.316|
|map_set_4000.sm|baseline|11.493|5.337|
|map_set_4000.sm|p1|11.560|4.729|
|map_set_4000.sm|p2|11.592|4.831|
|map_versions_1000.sm|baseline|12.100|4.899|
|map_versions_1000.sm|p1|11.874|5.408|
|map_versions_1000.sm|p2|12.223|5.807|
|map_versions_16000.sm|baseline|12.238|5.113|
|map_versions_16000.sm|p1|12.091|4.622|
|map_versions_16000.sm|p2|12.447|5.621|
|map_versions_32000.sm|baseline|11.752|4.666|
|map_versions_32000.sm|p1|11.702|4.649|
|map_versions_32000.sm|p2|11.467|4.748|
|map_versions_4000.sm|baseline|12.514|5.436|
|map_versions_4000.sm|p1|11.366|5.159|
|map_versions_4000.sm|p2|12.745|6.030|
|record_with_1000.sm|baseline|13.003|5.218|
|record_with_1000.sm|p1|11.803|4.862|
|record_with_1000.sm|p2|12.885|4.674|
|record_with_16000.sm|baseline|12.574|5.013|
|record_with_16000.sm|p1|14.432|5.405|
|record_with_16000.sm|p2|14.649|6.369|
|record_with_32000.sm|baseline|12.762|5.121|
|record_with_32000.sm|p1|11.896|4.514|
|record_with_32000.sm|p2|13.331|6.020|
|record_with_4000.sm|baseline|16.386|6.539|
|record_with_4000.sm|p1|13.899|6.840|
|record_with_4000.sm|p2|14.511|6.621|
|seq_push_1000.sm|baseline|15.158|5.922|
|seq_push_1000.sm|p1|12.338|6.019|
|seq_push_1000.sm|p2|12.569|5.834|
|seq_push_16000.sm|baseline|12.527|6.013|
|seq_push_16000.sm|p1|11.779|5.034|
|seq_push_16000.sm|p2|11.863|4.654|
|seq_push_32000.sm|baseline|11.758|5.990|
|seq_push_32000.sm|p1|12.608|4.695|
|seq_push_32000.sm|p2|11.796|5.171|
|seq_push_4000.sm|baseline|11.439|4.408|
|seq_push_4000.sm|p1|11.949|4.894|
|seq_push_4000.sm|p2|11.966|4.644|
|seq_read_1000.sm|baseline|10.971|5.278|
|seq_read_1000.sm|p1|11.802|4.462|
|seq_read_1000.sm|p2|11.629|4.608|
|seq_read_16000.sm|baseline|14.295|5.268|
|seq_read_16000.sm|p1|13.831|4.772|
|seq_read_16000.sm|p2|13.858|5.259|
|seq_read_32000.sm|baseline|12.920|5.920|
|seq_read_32000.sm|p1|12.671|4.956|
|seq_read_32000.sm|p2|11.208|4.440|
|seq_read_4000.sm|baseline|11.707|4.619|
|seq_read_4000.sm|p1|11.352|4.964|
|seq_read_4000.sm|p2|12.193|4.753|
|state10_16000.sm|baseline|11.296|4.621|
|state10_16000.sm|p1|11.672|4.720|
|state10_16000.sm|p2|11.577|4.717|
|state10_32000.sm|baseline|13.724|6.575|
|state10_32000.sm|p1|15.450|6.799|
|state10_32000.sm|p2|16.227|5.479|
|state10_8000.sm|baseline|12.638|5.039|
|state10_8000.sm|p1|13.154|5.037|
|state10_8000.sm|p2|14.189|5.270|
|state5_16000.sm|baseline|14.526|6.344|
|state5_16000.sm|p1|14.441|6.747|
|state5_16000.sm|p2|15.759|7.621|
|state5_32000.sm|baseline|14.846|7.229|
|state5_32000.sm|p1|14.995|5.169|
|state5_32000.sm|p2|13.627|5.308|
|state5_8000.sm|baseline|12.048|4.560|
|state5_8000.sm|p1|12.024|5.738|
|state5_8000.sm|p2|11.887|4.966|
|state_record_map_1000.sm|baseline|12.115|4.787|
|state_record_map_1000.sm|p1|13.593|5.046|
|state_record_map_1000.sm|p2|12.067|5.101|
|state_record_map_16000.sm|baseline|12.450|5.215|
|state_record_map_16000.sm|p1|11.702|5.082|
|state_record_map_16000.sm|p2|11.919|4.899|
|state_record_map_32000.sm|baseline|12.397|5.544|
|state_record_map_32000.sm|p1|13.895|5.401|
|state_record_map_32000.sm|p2|12.824|5.108|
|state_record_map_4000.sm|baseline|13.461|5.561|
|state_record_map_4000.sm|p1|13.964|5.571|
|state_record_map_4000.sm|p2|13.430|5.308|
|state_record_seq_1000.sm|baseline|13.853|5.841|
|state_record_seq_1000.sm|p1|13.596|4.611|
|state_record_seq_1000.sm|p2|12.854|5.290|
|state_record_seq_16000.sm|baseline|11.856|5.739|
|state_record_seq_16000.sm|p1|11.152|4.954|
|state_record_seq_16000.sm|p2|12.152|4.705|
|state_record_seq_32000.sm|baseline|12.578|6.085|
|state_record_seq_32000.sm|p1|12.981|4.792|
|state_record_seq_32000.sm|p2|11.798|5.576|
|state_record_seq_4000.sm|baseline|12.564|5.208|
|state_record_seq_4000.sm|p1|12.891|5.863|
|state_record_seq_4000.sm|p2|13.405|5.621|
|text_scan_1000.sm|baseline|12.943|5.497|
|text_scan_1000.sm|p1|11.725|4.870|
|text_scan_1000.sm|p2|13.154|4.928|
|text_scan_16000.sm|baseline|11.349|5.121|
|text_scan_16000.sm|p1|11.877|5.247|
|text_scan_16000.sm|p2|12.029|4.893|
|text_scan_32000.sm|baseline|11.428|5.135|
|text_scan_32000.sm|p1|12.005|5.198|
|text_scan_32000.sm|p2|12.177|5.876|
|text_scan_4000.sm|baseline|13.504|5.529|
|text_scan_4000.sm|p1|13.306|5.765|
|text_scan_4000.sm|p2|14.098|6.031|

### O0/O1 controlled-observation parity

run-smc has its own default quotas and no application host profile. This is not elevated-envelope O1 performance evidence.

- lex_calls baseline: exact output/exit parity=True; O0 exit=1, O1 exit=1; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-lex_calls-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-lex_calls-O1.out.
- lex_calls p1: exact output/exit parity=True; O0 exit=1, O1 exit=1; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-lex_calls-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-lex_calls-O1.out.
- lex_calls p2: exact output/exit parity=True; O0 exit=1, O1 exit=1; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-lex_calls-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-lex_calls-O1.out.
- map_get baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-map_get-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-map_get-O1.out.
- map_get p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-map_get-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-map_get-O1.out.
- map_get p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-map_get-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-map_get-O1.out.
- map_set baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-map_set-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-map_set-O1.out.
- map_set p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-map_set-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-map_set-O1.out.
- map_set p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-map_set-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-map_set-O1.out.
- map_versions baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-map_versions-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-map_versions-O1.out.
- map_versions p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-map_versions-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-map_versions-O1.out.
- map_versions p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-map_versions-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-map_versions-O1.out.
- record_with baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-record_with-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-record_with-O1.out.
- record_with p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-record_with-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-record_with-O1.out.
- record_with p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-record_with-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-record_with-O1.out.
- seq_push baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-seq_push-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-seq_push-O1.out.
- seq_push p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-seq_push-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-seq_push-O1.out.
- seq_push p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-seq_push-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-seq_push-O1.out.
- seq_read baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-seq_read-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-seq_read-O1.out.
- seq_read p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-seq_read-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-seq_read-O1.out.
- seq_read p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-seq_read-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-seq_read-O1.out.
- state_record_map baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-state_record_map-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-state_record_map-O1.out.
- state_record_map p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-state_record_map-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-state_record_map-O1.out.
- state_record_map p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-state_record_map-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-state_record_map-O1.out.
- state_record_seq baseline: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-state_record_seq-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-state_record_seq-O1.out.
- state_record_seq p1: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-state_record_seq-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-state_record_seq-O1.out.
- state_record_seq p2: exact output/exit parity=True; O0 exit=0, O1 exit=0; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-state_record_seq-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-state_record_seq-O1.out.
- text_scan baseline: exact output/exit parity=True; O0 exit=1, O1 exit=1; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-text_scan-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-baseline-text_scan-O1.out.
- text_scan p1: exact output/exit parity=True; O0 exit=1, O1 exit=1; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-text_scan-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p1-text_scan-O1.out.
- text_scan p2: exact output/exit parity=True; O0 exit=1, O1 exit=1; logs /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-text_scan-O0.out, /home/WSL_USER/shf-r-comparison-20261015/phase-logs/parity-run-p2-text_scan-O1.out.

## F. Interpretation and limitations

Section J gives the final analysis; numerical tables above derive only from saved runs. Small absolute differences and single-host measurements are not portable guarantees. Known historical container results used a Xeon host rather than this Core i5 WSL host; compare scaling and matched-revision ratios, not absolute milliseconds. Original internal wall_ms is retained alongside external process wall time.

MiniLang lexer/parser original sources and frozen inputs: NOT RUN unless separately identified in this experiment. State5/State10 cover repeated mixed scalar/Sequence field updates. A separately recorded mixed-update generator and a Record+nested-Sequence benchmark were not identified: NOT RUN as independent families. No replacement workload is labeled MiniLang.

Fast-path move/fallback counters are test-only in the existing VM and are not exposed by this release CLI; fast-path activation counts: NOT MEASURED. Timing improvement alone is not a direct proof of activation.

## G. Repository preservation

See repository-preservation.json and active-before/after snapshots. No GitHub mutations, source changes, branch changes in the active repository, quota changes, installation, or Checkpoint B implementation. Disposable checkouts and caches retained.

## H. Artifact and failure inventory

### Frozen source and input SHA-256

|Path|SHA-256|
|---|---|
|`workloads/lex_calls_1000.sm`|`67ffa8079d7435929176722a4e6539efa221933380fecfd1f3c7ef8dfad5022b`|
|`workloads/lex_calls_16000.sm`|`be0c2cfc2bc812713f7805f099d8acfbb10acda1eb4b844215369aaa18f228d3`|
|`workloads/lex_calls_32000.sm`|`e52cb563a561599ae4bc6a7c123f263f8bab57c1065e635f92e7d2dad96dd820`|
|`workloads/lex_calls_4000.sm`|`4893032c43b13619e18225f86d585f73992deee3a1bde0de5c357996d995eaa0`|
|`workloads/map_get_1000.sm`|`d0678d67cd64b0ecfc57d767821f3d0663067bf774b9a00b7dc241ba76d47eec`|
|`workloads/map_get_16000.sm`|`faf8c584a58dfbee36f72b21aa6960f6805daa439d595c1ea8a93c280bd2068c`|
|`workloads/map_get_32000.sm`|`e76e64a64aa9f8cdfb38637a4fc2a11e073d5fd0e94afb59d244c426c55e962b`|
|`workloads/map_get_4000.sm`|`7e724866c6db319527822ee2c442e55ac69a72bd410d21dc4eb0fc049a794b8e`|
|`workloads/map_set_1000.sm`|`36aef4c8b5e6519b1aeb5d3bc686e1d80453f82c49023fc44b4744ce0c236e58`|
|`workloads/map_set_16000.sm`|`d3edcec2de6da43e3b038ff652f8063a21bc43cd0c014b753c2455f056d9a082`|
|`workloads/map_set_32000.sm`|`bff2ef5f5d95f6244dd09fbc7ff39161d2303ee935947a77baea1d3249f2f913`|
|`workloads/map_set_4000.sm`|`1902587111c50671684f6b0850c9ed39cd1a21770fd54675ea799b6fde923275`|
|`workloads/map_versions_1000.sm`|`106715411bf413666a2f0f4b0b3bc3ab95c8423546b431495dca66345ca3ac76`|
|`workloads/map_versions_16000.sm`|`24b4214855694a80a8f64d0dec5a1fb9f87c2f1c8bf5c1b27a575c29a9d0b6b2`|
|`workloads/map_versions_32000.sm`|`e6e6bc7d20849dfade7f8106696f4218853f8de489a8fef447a658575a92688c`|
|`workloads/map_versions_4000.sm`|`1543bb03c77073cd26e719570b1e9a676619bfb4ae1f655db689f857578b0972`|
|`workloads/record_with_1000.sm`|`9d263b2f7b30de5b6fef5e05d1f022346c689454c0988e7e949f348ff2ee6a76`|
|`workloads/record_with_16000.sm`|`2e6c13e256071554070771503181aae7c7f8a86e592bb08dc7c0f94c870f7e9d`|
|`workloads/record_with_32000.sm`|`81bae289194b86c818ffe2a134885622b0ef420d1a448da5ddb9b3e1fab78902`|
|`workloads/record_with_4000.sm`|`0ef1ff39645977745a1a58a7c5828995dcc9f5cdb983adb0be2ccc2047d966b5`|
|`workloads/root/input_1000.txt`|`a7a159655a60bdd965de6be15478250a713f8b8957fb070a084519239a26ad36`|
|`workloads/root/input_16000.txt`|`a83565fc958e16cd324c63e542b12879c606bb2851bacca07a16c70cef3aed5e`|
|`workloads/root/input_32000.txt`|`206d78291eecc6e0a6a343b057f91d0cf84c79e59be92a86dae5440fdfd38c4a`|
|`workloads/root/input_4000.txt`|`ee99e165c68d3a7db7a3c4494fc9359b5b986c247b7df29cff6b668c8e7cc827`|
|`workloads/seq_push_1000.sm`|`043a756d7fa5310ab62c738478c75ffcb16bf131dc7fd91a461c6c6c87305b05`|
|`workloads/seq_push_16000.sm`|`792720d92d1a5bf139a978b3eb45f0417eb4552d90af3156234fd2940cac077b`|
|`workloads/seq_push_32000.sm`|`aee009755397173d26ec7247a6925b227d5251ad575ec7e3396ea432e2e79d5d`|
|`workloads/seq_push_4000.sm`|`7807e2d9c3290f2ef025feba34374276718f2a301d3e07edd68ad6642be7cdee`|
|`workloads/seq_read_1000.sm`|`167d79bd493ee2f16e5c2f9953c286fa6ad0442ae919baedc565249efec70e48`|
|`workloads/seq_read_16000.sm`|`71965967e23752a026ce3c2895e211064eebbba30f3602b64e6956cccb747b4d`|
|`workloads/seq_read_32000.sm`|`bbe3940cd25336acac9f4ed49e0748c38043ec47f652587cf7a9aa944284355c`|
|`workloads/seq_read_4000.sm`|`e8a631dadaf296a0c83d8e9d38e707d2afbbaeae4d5ad545071cad09eb44e5e0`|
|`workloads/state10_16000.sm`|`d211599f53a233bf154198ec555afa107580761793650b69722a66550b7551fb`|
|`workloads/state10_32000.sm`|`fb6190ea28532aa4008ae81707fdca3d2e4adae88310d1dbece79d299afb9e1c`|
|`workloads/state10_8000.sm`|`57a53a3925be7750b6efe47cfa6521bc24a20602cc3929188a6a061004b1b5c2`|
|`workloads/state5_16000.sm`|`d8bc67232e10bb5b37c59b969662103e885afb980d4762b11482edbe483a2d31`|
|`workloads/state5_32000.sm`|`b64f8edeb02fa795f1db5efccdf09a60dbac833a9f8f5016600aa318a506a8b0`|
|`workloads/state5_8000.sm`|`4eace9791dd67d20621d2e8636d806894606dc35e56025c49eb90c3af097b462`|
|`workloads/state_record_map_1000.sm`|`9c1de5079ddd13f86e62027f3ff379a2eda871be62bc450faadef759271b0e9d`|
|`workloads/state_record_map_16000.sm`|`6e2eaeb9d1e12fbb6ad041b8c9ff68c4dca7ffbd9cc1113d437a91ff0651fd30`|
|`workloads/state_record_map_32000.sm`|`335d77fd0e9994b6b394b7712bd2b4aa5aa853d89361c42bcfd2a3db049b5e99`|
|`workloads/state_record_map_4000.sm`|`ae472e9b5cf79b44dacb0f5550e97bc2facee6c85f98b6d3e1a739a3c03e33c2`|
|`workloads/state_record_seq_1000.sm`|`dedf9d01048d6156439442346cf8e5fb0ebd458e4009d7edef126af878d8e506`|
|`workloads/state_record_seq_16000.sm`|`1cd703a39f8f30c527e4f3a3fbdd81ee72e7d31e6cb991a7f1557efaa0df5ce7`|
|`workloads/state_record_seq_32000.sm`|`50d459b3cbbe403d7aeee9c918ef7c43bab2cfe0d95d75c7493aad6c32ff9184`|
|`workloads/state_record_seq_4000.sm`|`4efe4130f05b373c453927e22c52a9311f4ef09a6976724ba6b285dec04292fb`|
|`workloads/text_scan_1000.sm`|`c6ef82b1a8cc6c74308c9836bf72fbb390cf383a5d65b9390f52f48316e0477f`|
|`workloads/text_scan_16000.sm`|`7852911a2fd2683b091dedfbe3d9d6029366cc2639eb491ef63372045a92f002`|
|`workloads/text_scan_32000.sm`|`7eafdeb8f4e67e7f1220f7abfe768bbaade40092de402e04c326480a932c139f`|
|`workloads/text_scan_4000.sm`|`d035736c7b111a1e2b1a6e07438ba97c3f0bfdfc64fa6e07e81ce81b7426597a`|
|`workloads/tuple_loop_1000.sm`|`0aa457bf9042e5de498c3fd24ad30856dc8345065239a97ac1c4eec384351e18`|
|`workloads/tuple_loop_16000.sm`|`86858fb927165d1dd0fe3f640ac2ac8e6ce1fae4e653f56ba853245ec207ff7b`|
|`workloads/tuple_loop_32000.sm`|`21ae97b76c9e91ca097027affaa555d2ed12e3679c9f9a5935ed148207b6a4b2`|
|`workloads/tuple_loop_4000.sm`|`d6a11522a95052f438e8638f1d69f712540db730b8cd4c2d5d3c0c80b92367ae`|

The original generator also writes tuple_loop; it is retained for provenance but is outside the requested timing families. Original text inputs have floor(N/12)*12 bytes, following the generator exactly.

### All timeout attempts (including warm-up)

- map_get N=32000 baseline, trial=-1, 120001.9 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_get N=32000 baseline, trial=0, 120001.4 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_get N=32000 baseline, trial=1, 120002.1 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_get N=32000 baseline, trial=2, 120001.4 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_versions N=32000 baseline, trial=-1, 120002.0 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_versions N=32000 baseline, trial=0, 120001.7 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_versions N=32000 baseline, trial=1, 120001.3 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- map_versions N=32000 baseline, trial=2, 120001.7 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=16000 baseline, trial=-1, 120001.5 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=16000 baseline, trial=0, 120001.6 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=16000 baseline, trial=1, 120001.5 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=16000 baseline, trial=2, 120001.4 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=32000 baseline, trial=-1, 120001.9 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=32000 baseline, trial=0, 120002.6 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=32000 baseline, trial=1, 120001.4 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.
- state_record_map N=32000 baseline, trial=2, 120001.7 ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.

### E2 activation test

```text
   Compiling proc-macro2 v1.0.107
   Compiling quote v1.0.47
   Compiling serde_core v1.0.229
   Compiling syn v3.0.6
   Compiling zmij v1.0.23
   Compiling itoa v1.0.18
   Compiling memchr v2.8.3
   Compiling serde_derive v1.0.229
   Compiling sm-diagnostic v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-diagnostic)
   Compiling serde_json v1.0.151
   Compiling sm-format v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-format)
   Compiling serde v1.0.229
   Compiling ton618-core v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/ton618-core)
   Compiling sm-profile v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-profile)
   Compiling sm-runtime-core v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-runtime-core)
   Compiling sm-front v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-front)
   Compiling prom-refs v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/prom-refs)
   Compiling prom-abi v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/prom-abi)
   Compiling prom-cap v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/prom-cap)
   Compiling sm-verify v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-verify)
   Compiling sm-ir v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-ir)
   Compiling semantic-core-quad v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/semantic-core-quad)
   Compiling sm-emit v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-emit)
   Compiling sm-vm v0.1.0 (/home/WSL_USER/shf-r-comparison-20261015/p2/crates/sm-vm)
    Finished `release` profile [optimized] target(s) in 1m 40s
     Running unittests src/lib.rs (/home/WSL_USER/shf-r-comparison-20261015/target-p2/release/deps/sm_vm-2001b3bd14878652)

running 1 test
test semcode_vm::tests::shf_p3_consume_tests::e2_fast_path_activation_and_moves_count ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 207 filtered out; finished in 0.00s

     Running tests/vm_opcode_profile.rs (/home/WSL_USER/shf-r-comparison-20261015/target-p2/release/deps/vm_opcode_profile-6412971032a8e6d2)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/vm_opcode_profile_workloads.rs (/home/WSL_USER/shf-r-comparison-20261015/target-p2/release/deps/vm_opcode_profile_workloads-9bba91c4195de5bd)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

This existing test is independent of timed CLI measurements. It covers State5 N=100 (moves >=100, fallbacks=0); it does not instrument the timed State5/State10 runs.

### Tracked tree preservation

```json
{
  "collected_utc": "2026-10-15T19:15:42.019394+00:00",
  "active_repository": "C:/Users/OWNER_USER/Desktop/EXOcode/Semantic_ui_dna2_3b_artifact_v1",
  "active_snapshot_unchanged": true,
  "active_before": {
    "head": "966816345cd3702b8cc40969b4e8b35e1bf1d17f",
    "originMain": "188dec7eddfafaab5926af2d30f528bfe3d89a2c",
    "status": [
      "?? \".codex-remote-attachments/01a13f06-c44d-73a3-ba2a-b3483e73280c/b70f8a42-80a6-453b-8e7f-c910bf4947b9/1-\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260-\\320\\265\\320\\262\\321\\200\\320\\276\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260.pdf\""
    ],
    "diff": [],
    "untracked": [
      "\".codex-remote-attachments/01a13f06-c44d-73a3-ba2a-b3483e73280c/b70f8a42-80a6-453b-8e7f-c910bf4947b9/1-\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260-\\320\\265\\320\\262\\321\\200\\320\\276\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260.pdf\""
    ]
  },
  "active_after": {
    "head": "966816345cd3702b8cc40969b4e8b35e1bf1d17f",
    "originMain": "188dec7eddfafaab5926af2d30f528bfe3d89a2c",
    "status": [
      "?? \".codex-remote-attachments/01a13f06-c44d-73a3-ba2a-b3483e73280c/b70f8a42-80a6-453b-8e7f-c910bf4947b9/1-\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260-\\320\\265\\320\\262\\321\\200\\320\\276\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260.pdf\""
    ],
    "diff": [],
    "untracked": [
      "\".codex-remote-attachments/01a13f06-c44d-73a3-ba2a-b3483e73280c/b70f8a42-80a6-453b-8e7f-c910bf4947b9/1-\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260-\\320\\265\\320\\262\\321\\200\\320\\276\\320\\261\\321\\200\\320\\276\\320\\275\\320\\267\\320\\260.pdf\""
    ]
  },
  "remote_main_after_fetch": "188dec7eddfafaab5926af2d30f528bfe3d89a2c",
  "remote_main_final": "188dec7eddfafaab5926af2d30f528bfe3d89a2c",
  "isolated_origin_main_final": "188dec7eddfafaab5926af2d30f528bfe3d89a2c",
  "checkouts": {
    "baseline": {
      "head": "94c5c50d16c3f2efc7691456755461bedae83b18",
      "status": "",
      "lock_unchanged": true,
      "binary_unchanged": true,
      "quota_source_blob": "a942eaed37437b155ec921137ef9ba198ff5a008",
      "cli_source_blob": "9fa7190d77e8a97b4e42f29fde73abc50f37f708"
    },
    "p1": {
      "head": "758738a2edf0e984d6067fb372f003a381723d02",
      "status": "",
      "lock_unchanged": true,
      "binary_unchanged": true,
      "quota_source_blob": "a942eaed37437b155ec921137ef9ba198ff5a008",
      "cli_source_blob": "9fa7190d77e8a97b4e42f29fde73abc50f37f708"
    },
    "p2": {
      "head": "188dec7eddfafaab5926af2d30f528bfe3d89a2c",
      "status": "",
      "lock_unchanged": true,
      "binary_unchanged": true,
      "quota_source_blob": "a942eaed37437b155ec921137ef9ba198ff5a008",
      "cli_source_blob": "9fa7190d77e8a97b4e42f29fde73abc50f37f708"
    }
  },
  "frozen_input_mismatches": []
}
```


Standalone O0 SemCode byte identity: 46/46 workload artifacts have identical hashes across all three revisions. Full hashes in artifact-hashes.json; identical source is not assumed to imply byte identity without this comparison.


## I. Runtime counters and peak RSS

Counters shown are actual P2 measured observations; cross-revision equality/availability is reported in section D. RSS columns are maximum observed process peak across the three measured repetitions, not allocation traffic or a heap bound.

|Workload|N|P2 Steps|Calls|Peak frames|Effects|Baseline RSS KiB|P1 RSS KiB|P2 RSS KiB|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|lex_calls|1000|34052|996|2|1|7600|7768|7580|
|lex_calls|4000|136552|3996|2|1|7764|7680|7780|
|lex_calls|16000|546552|15996|2|1|7760|7836|7932|
|lex_calls|32000|559809|16384|2|1|7728|7848|7824|
|map_get|1000|39023|0|1|0|8124|7924|7916|
|map_get|4000|156023|0|1|0|11612|8428|8360|
|map_get|16000|624023|0|1|0|24632|10528|10684|
|map_get|32000|1248023|0|1|0|NOT MEASURED|13496|13636|
|map_set|1000|14017|0|1|0|7960|7644|7932|
|map_set|4000|56017|0|1|0|10304|8172|8368|
|map_set|16000|224017|0|1|0|24644|10696|10708|
|map_set|32000|448017|0|1|0|39192|13604|13532|
|map_versions|1000|30035|0|1|0|8500|7872|8008|
|map_versions|4000|120035|0|1|0|12412|9032|9000|
|map_versions|16000|480035|0|1|0|31192|13468|13496|
|map_versions|32000|960035|0|1|0|NOT MEASURED|19672|19516|
|record_with|1000|25019|0|1|0|7616|7496|7668|
|record_with|4000|100019|0|1|0|7408|7728|7724|
|record_with|16000|400019|0|1|0|7508|7728|7628|
|record_with|32000|800019|0|1|0|7616|7496|7632|
|seq_push|1000|13015|0|1|0|7672|7712|7620|
|seq_push|4000|52015|0|1|0|7788|7852|7744|
|seq_push|16000|208015|0|1|0|8516|8548|8420|
|seq_push|32000|416015|0|1|0|9608|9660|9664|
|seq_read|1000|28023|0|1|0|7672|7592|7576|
|seq_read|4000|112023|0|1|0|7704|7772|7696|
|seq_read|16000|448023|0|1|0|8524|8504|8648|
|seq_read|32000|896023|0|1|0|9688|9728|9672|
|state10|8000|224026|0|1|0|10216|10128|8016|
|state10|16000|448026|0|1|0|14656|14596|8612|
|state10|32000|896026|0|1|0|26188|25084|9828|
|state5|8000|184021|0|1|0|10196|10020|7984|
|state5|16000|368021|0|1|0|14720|15140|8740|
|state5|32000|736021|0|1|0|25908|25092|9856|
|state_record_map|1000|25034|0|1|0|9632|7660|7892|
|state_record_map|4000|100034|0|1|0|16356|8440|8480|
|state_record_map|16000|400034|0|1|0|NOT MEASURED|11036|11016|
|state_record_map|32000|800034|0|1|0|NOT MEASURED|14536|14556|
|state_record_seq|1000|20018|0|1|0|7796|7956|7648|
|state_record_seq|4000|80018|0|1|0|8688|8764|7664|
|state_record_seq|16000|320018|0|1|0|16352|14628|8524|
|state_record_seq|32000|640018|0|1|0|26408|25464|9680|
|text_scan|1000|25169|0|1|1|7676|7588|7744|
|text_scan|4000|100919|0|1|1|7536|7616|7716|
|text_scan|16000|403919|0|1|1|7668|7492|7636|
|text_scan|32000|807818|0|1|1|7744|7892|7600|
## J. Technical conclusions and OWNER checkpoint

Qualification collected on 2026-10-15T19:20:33.025465+00:00. This is an independent read-only experiment, not an implementation, merge, issue-closure, release or self-hosting-completion authorization.

### Observed improvements — primary three-sample series

|Workload|N|Baseline median ms|P1 median ms|P2 median ms|B/P2 speedup|
|---|---:|---:|---:|---:|---:|
|map_set|32000|85752.31|130.90|159.01|539.28x|
|state_record_seq|32000|27026.57|25150.68|186.38|145.00x|
|state5|32000|27744.32|26916.90|269.05|103.12x|
|state10|32000|28172.92|27815.31|427.03|65.97x|

**CONFIRMED IMPROVEMENT on this corpus:** baseline map_set fitted p=1.901; the optimized series is not quadratic over the measured range. P1/P2 global fits (0.522/0.563) are depressed by startup and noisy small-size samples, not a claim of sublinear Map construction. At 16k→32k their primary adjacent slopes are 0.972/0.961. The supplemental same-input Map curve is retained separately; no original sample was replaced.

**CONFIRMED IMPROVEMENT:** state_record_seq fitted p changes from 2.000 (baseline), 2.008 (P1) to 0.801 (P2). State5 changes 2.015/1.998→0.836; State10 1.971/2.066→0.854. These are empirical CLI fits on 3–4 sizes, not deterministic worst-case complexity proofs. Fixed startup/compile/admission costs depress optimized whole-range exponents.

P1 alone does not resolve Record+Sequence amplification: its measured behavior remains approximately quadratic. E1/E2 produces the large improvement in P2.

### Reproduced regressions and uncertainty — separate six-pair confirmation

The same frozen sources, CLI flags, quotas, binary hashes and 120-second timeout were reused. Six measured P1/P2 pairs alternate execution order after warm-up. These are additional observations, not replacements for section B. No baseline timeout was extended or converted into a runtime.

|Workload|N|P1 median ms [range]|P2 median ms [range]|Ratio of medians P2/P1|Pairs P2 slower|Assessment|
|---|---:|---:|---:|---:|---:|---|
|lex_calls|16000|132.53 [122.09–209.38]|168.90 [164.34–259.94]|1.274x (+27.4%)|5/6|Repeated median penalty; noisy pair/range evidence|
|map_get|32000|291.11 [260.75–405.59]|394.59 [331.19–469.37]|1.355x (+35.5%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|map_set|1000|11.36 [10.88–12.17]|13.07 [10.49–15.15]|1.151x (+15.1%)|5/6|Repeated median penalty; noisy pair/range evidence|
|map_set|4000|19.51 [19.02–20.84]|24.37 [22.58–26.97]|1.249x (+24.9%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|map_set|16000|67.66 [63.64–80.95]|81.57 [78.74–105.46]|1.206x (+20.6%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|map_set|32000|159.31 [136.99–317.39]|218.50 [170.34–302.59]|1.372x (+37.2%)|5/6|Repeated median penalty; noisy pair/range evidence|
|map_versions|32000|281.57 [252.27–384.26]|334.67 [325.75–381.60]|1.189x (+18.9%)|5/6|Repeated median penalty; noisy pair/range evidence|
|record_with|32000|174.53 [148.03–229.20]|299.58 [234.76–326.32]|1.716x (+71.6%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|seq_push|32000|75.77 [75.05–86.04]|110.59 [101.86–124.80]|1.460x (+46.0%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|seq_read|32000|161.30 [148.34–211.37]|235.96 [207.46–273.81]|1.463x (+46.3%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|state_record_map|32000|276.53 [237.00–363.23]|354.41 [301.68–393.43]|1.282x (+28.2%)|6/6|CONFIRMED direction; magnitude host/noise dependent|
|text_scan|32000|244.44 [206.51–289.91]|287.62 [255.05–394.59]|1.177x (+17.7%)|6/6|CONFIRMED direction; magnitude host/noise dependent|

**CONFIRMED REGRESSION:** P2 is slower than P1 in all six confirmation pairs for seq_push, seq_read, scalar record_with, text_scan, map_get, state_record_map and map_set at 4k/16k. Approximate ratio-of-medians penalties at 32k are +46% seq_push, +46% seq_read, +72% scalar record_with and +18% text_scan. Primary-series differences point in the same direction. Treat these as real findings; the optimized target workloads do not erase them.

**INCONCLUSIVE precise magnitudes / noisy controls:** several ranges overlap, single pairs reverse in map_set 1k/32k, map_versions and lex_calls. Main map_set 4k timing has a wide range; the separate six-sample curve is more stable there. Three/six samples on a shared laptop do not establish a portable penalty or a zero-overhead guarantee. No new quadratic behavior was demonstrated for these linear families.

The experiment does not isolate the cause of the P2 penalties: CLI time combines compiler, verifier, planner and dispatch/runtime costs. It is not evidence that a particular planner loop is responsible.

### Correctness, admission and resource findings

- Main matrix: 552 invocations (138 warm-ups + 414 measured); six negative controls bring the initial total to 558. Outcomes: 524 ok, 16 TIMEOUT, 12 Calls quota failures, three Steps control failures, three capability denials. Supplemental confirmation adds 168 successful invocations (24 warm-ups + 144 measured). Total runtime invocations: 726. Raw measurements preserve every result.
- No assertion failure, normalized runtime-metrics/counter difference, stdout difference, audit-line difference or deterministic error-class/text difference was found among completed comparable runs. All 46 source/size groups have completed observations; four groups lack baseline completion at the large size and remain NOT COMPARABLE against baseline there.
- Standalone compile/verify: 552 compile calls and 552 verify calls all exit 0. All 138 revision/input groups reproduce their artifact hash across four compilations; all 46 O0 workload artifacts are byte-identical across the three revisions. These are standalone emitted artifacts of the frozen inputs; ephemeral in-process artifacts inside smc run were not separately exported or hashed.
- O0/O1 controls: all 60 compilations succeed. Eight pure families × three revisions = 24 successful parity pairs (48 executions), with identical outputs and exit status. text_scan/lex_calls account for six additional pairs (12 executions) returning identical Host ABI FsRead Unavailable errors: their O0/O1 successful application behavior is NOT RUN through run-smc, whose host does not provide these application operations. Do not count these as successful functional parity.
- E2 activation: existing release unit test e2_fast_path_activation_and_moves_count passes (1 test; 207 filtered). Its source is State5 N=100 and asserts moves >=100 and fallbacks=0. This directly confirms that fixture only. Per-timed-run move/fallback counts and direct State10 activation counts are NOT MEASURED; State10 timing/scaling is consistent with the intended fast path but is not a counter proof.
- No new functional/admission/capability defect was reproduced by this corpus. Confirmed performance regressions above remain findings. This is not an exhaustive VM ownership or failure-path audit.

**KNOWN RESOURCE LIMITATION:** lex_calls N=32000 fails on every revision with Calls limit=16384, used=16385 under max_steps=200000000. Without the Steps override all three fail earlier with Steps limit=100000, used=100001, at counters steps=100000, calls=2926, peak_frames=2, effect_calls=1. max_calls remains 16384 in both configurations. The default-Steps run therefore does not reach the Calls boundary and is not a successful Calls test.

**Capability safety control:** unchanged text_scan under pure is denied before host dispatch on all three revisions: FsRead MissingCapability, steps=2, calls=0, frames=1, effect_calls=0. No capability was added by the Steps override.

Source-confirmed defaults not exposed in full by the metrics schema: max_registers=4096, max_symbol_table=16384, max_debug_symbols_per_function=8192. Runtime-core and CLI source Git blob IDs are identical across all three checkouts (repository-preservation.json). Explicit runtime metrics retain max_steps, max_calls, max_frames, max_stack_depth and max_effect_calls. This corpus does not sweep the register/symbol/frame boundary conditions.

**TIMEOUT inventory:** baseline map_get 32000; baseline map_versions 32000; baseline state_record_map 16000 and 32000. Each has one warm-up and three measured 120-second timeouts (16 total). No speedup is calculated from those failed cases. Assertions for those exact baseline invocations did not complete.

### Historical methodology reconciliation

Original source and generator: [Semantic #2030 comment 6168428649](https://github.com/skulmakov-oss/Semantic/issues/2030#issuecomment-6168428649), cached verbatim with its generator SHA. The original used a Linux container on Xeon 2.10 GHz/4 vCPU, not this Core i5 WSL2 host. Both use pinned Rust 1.97.1 release builds, self-asserting sources, original application profiles/inputs, trusted-compiler, Steps=200000000 and default Calls. This experiment adds explicit --locked/--offline, separate immutable checkouts/targets, process wall time, RSS and matched three-revision execution.

Original timing was metrics nondeterministic.wall_ms (application command including compilation and verification). This report primary table uses external process wall time including CLI startup and teardown; original internal timing is retained in measurements.jsonl and summary.csv. Neither is VM-only.

|Original family N=32000|Historical baseline internal ms|This host baseline internal median ms|This host external median ms|
|---|---:|---:|---:|
|map_set|55262|85743.41|85752.31|
|state_record_seq|17073|27020.77|27026.57|

Differences in absolute historical milliseconds are not matched-host regressions: host/virtualization differ, historical raw JSONL is not supplied, and timing boundaries differ slightly. Workload identity, exact baseline source SHA, Rust version and release settings were checked; no workload was edited to force agreement. P1/P2 benefits here are derived from this host’s matched comparisons.

The historical State5/State10 documentation table does not provide the same complete host/build provenance. Its State10 3.45x final doubling is not reproduced by this host’s medians:
- state5: P2 16k→32k ratio 1.962x; observed sample ranges remain in section B.
- state10: P2 16k→32k ratio 1.779x; observed sample ranges remain in section B.

### Missing measurements and evidence limits

- VM-only execution, isolated in-process planner/verification phases and allocator traffic: NOT MEASURED. Separate compile/verify command medians are not subtracted from an application-run timing.
- Large-function planner amplification: NOT MEASURED. These generators grow loop data/iteration counts, not function-body size; the experiment cannot close a large-function planning concern.
- Original MiniLang lexer/parser source and frozen input manifest were not supplied/identified in the tracked corpus, issues #2030/#2037 or the checked known qualification folder. NOT RUN; no synthetic equivalent is mislabeled MiniLang.
- Repeated mixed scalar/Sequence updates are represented by the existing State5/State10 loops. A separate original mixed-update generator and a Record+nested-Sequence benchmark were not identified: NOT RUN as independent families. Plain nested-Sequence unit fixtures are not substituted for them.
- Peak RSS is observed process memory, including compiler/verifier/runtime and libraries, not total allocated bytes, an aggregate VM heap quota, or a future retained-version memory bound.
- Linux load averages are recorded per invocation; builds and timed runs are sequential. A Linux snapshot during long baseline execution showed only the benchmark as a sustained CPU consumer and no swap pressure. Windows host contention, CPU frequency/thermal state and scheduler noise are uncontrolled. Brief OS background maintenance was observed during builds, before timings; no software installation/update was initiated by this task. Timing ranges and paired reversals are preserved.

### Answers to the eight decision questions

1. Persistent SemMap: **yes empirically for the original Map construction workload/range**; do not generalize fitted sublinear slopes into a complexity guarantee.
2. E1/E2 Record+Sequence: **yes empirically**, with baseline/P1 approximately quadratic and P2 nonquadratic on this range, plus State5/10 controls.
3. Existing linear workloads without material regressions: **NO**. No new quadratic trend was established, but repeated constant-factor slowdowns are demonstrated.
4. State5/10 intended fast path: State5 N=100 activation directly tested; timed State5/10 activation counts not exposed by the release CLI. Large-run scaling improvements are observed, direct State10 move counters NOT MEASURED.
5. End-to-end visibility: **YES**, because primary timings are full CLI application runs.
6. Large-function planner overhead: **INCONCLUSIVE / NOT MEASURED**; no attribution from end-to-end deltas.
7. Cumulative Calls: **YES, a reproduced practical blocker** for the original helper-per-byte lex_calls input; MiniLang-specific ceiling remains historical, not independently reproduced here.
8. Supported follow-up: investigate P2 overhead on scalar record updates, sequence reads/pushes, text scanning and Map operations with phase/dispatch profiling. No storage redesign or quota-policy implementation is inferred from timings.

### Self-hosting and Checkpoint B recommendation

**Prioritize P3 — a separately approved bounded Calls override contract.** The hard cumulative ceiling still stops the original 32k lex_calls program even after the major copy-amplification fixes. Keep defaults, independent Calls semantics, verifier/capability behavior and accounting unchanged unless OWNER grants a specific contract/implementation GO. The toy workload does not establish the numeric cap required for a real self-hosting compiler; MiniLang evidence is still needed for that decision.

**P4 follows:** application-mode O1 execution under the same admitted configuration remains a separate contract gap. Standalone O0/O1 pure parity is observed; run-smc cannot supply the application filesystem host/envelope, and this experiment makes no claim about an O1 compiler-workload speedup.

**Additional VM optimization is evidence-supported, but focused:** repeated P2 penalties deserve a separately scoped profiling/optimization task. Preserve the large Record+Sequence benefit and deterministic counters; avoid another broad representation rewrite without locating the cost. It does not replace the demonstrated need to address the Calls contract.

Issues #1910, #2030 and #2037 were checked OPEN and were not edited. This evidence advances #2030’s comparative qualification and #2037’s resource decisions; it does not close either issue or establish #1910 self-hosting completion.

### Final read-only gate

PASS: active Windows HEAD, tracked diff/status and untracked list match the initial snapshot; all three detached checkouts are clean; frozen input hashes, lockfiles and built binaries match; remote main and isolated origin/main remain 188dec7eddfafaab5926af2d30f528bfe3d89a2c. No repository/GitHub settings, issues, PRs, source, quotas, dependencies or runtime were modified. All checkouts, targets and raw artifacts are retained. No Checkpoint B implementation started.

**STOP — EVIDENCE READY FOR OWNER REVIEW.**
