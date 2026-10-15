# Checkpoint B / P3 — implementation evidence

BASE: `188dec7eddfafaab5926af2d30f528bfe3d89a2c`
HEAD: `64ca9087c83bf7ac504899246c1e7c8b06062d0f`
Status: local broad qualification still running; no PR published yet.

## Completed

| Check | Result | Evidence |
|---|---|---|
| Red baseline CLI | expected failure, exit101 | red-existing-binary.json/log |
| Envelope integration |25PASS| green.json/log |
| Core unit Windows |17PASS|runtime-core.log|
| Core no-std Windows |PASS|no-std-windows.log|
| API guard without update |89PASS|api-check.json/log|
| WSL relevant packages |684PASS,0FAIL,1existing ignored|relevant-packages.json/log|
| WSL focused Clippy warnings denied |PASS|clippy-focused.json/log|
| Windows workspace check and Clippy |PASS|full-preflight.log (ongoing later stages)|
| Actual workspace fmt |37packagesPASS|full-preflight.log|
| Staged local Harness |PASS|precommit command output|
| Immutable BASE checker local committed diff |PASS|harness-base-exact.log|
| Initial CRLF provenance rejection |preserved expected diagnostic|harness-trusted-local.log,harness-provenance.json|
| Independent accounting/diff reviews |no findings|accounting-review.md|
| Frozen corpus integrity |54/54 each native and Windows mirror|frozen-integrity.json|
| Raw invalid SemCode |same exit1 UnsupportedVersion|invalid-semcode.json|

## A/B

Original source and input were unchanged. Exact main binary matches previous experiment manifest.
See AB.json for all hashes, commands, runtime metrics, exits and wall timings; baseline-provenance.json and oracle-check.json for independent checks.
A: raised Steps only -> Calls16384used16385. B: explicit Calls1000000 -> ok,Calls31992,Steps1093082,peakframes2,effects1. Both other effective quotas unchanged. Source assertion digits5332 matches independently counted input digits5332.
Standalone O0 artifact SHA256 is identical; both artifacts verify. Application runs compile/admit source independently; no direct export of their in-process artifact or VM-only timing was performed.
CLI timings are single observations of different termination points, not performance speedups.

## Limits

200M numeric boundary configuration tested;200M actual-call stress test NOT RUN. No aggregate heap or wall-clock bound, authentication or self-hosting completion claim. P4 and P2 performance fixes not started.

## Pending

Windows full workspace tests/remaining FullPreflight stages,7hell,then authorized Draft PR and exact-head hostedCI. No merge or release permission.
