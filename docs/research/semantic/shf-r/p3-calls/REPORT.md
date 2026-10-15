# P3 qualification handoff — Draft PR #2049

PR: https://github.com/skulmakov-oss/Semantic/pull/2049

## Checkpoint B / P3 implementation candidate

**Draft only. No OWNER MERGE GO or release authorization. Numeric contract remains subject to final OWNER contract review.**

Refs #1910, #2030, #2037. No automatic issue closure.

BASE: `188dec7eddfafaab5926af2d30f528bfe3d89a2c`
HEAD: `64ca9087c83bf7ac504899246c1e7c8b06062d0f`
Branch: `shf-r/p3-bounded-calls`

### Proposed public CLI contract

Application `smc run --envelope trusted-compiler` gains optional `--max-calls <N>`:
- Strict ASCII decimal, once, `1 <= N <= 200000000` and `N <= effective max_steps`.
- Omitted Steps means effective Steps=100000. Omitted Calls stays exactly 16384, including with a smaller explicit Steps budget.
- Steps never automatically raises Calls. Calls remains cumulative charged non-root Semantic invocations.
- All invalid argument categories fail before source compilation/admission/execution, with no metrics line.
- Existing two-argument `RuntimeQuotas::trusted_compiler` and `QuotaOverrideError` remain unchanged. New bounded method/error/constant are additive; only the runtime-core API snapshot changes.

The 200-million candidate ceiling matches the existing maximum Step count. Direct and closure CALL dispatches charge a Step before the sole non-root Calls charge, including recursion; root is exempt and builtins inline do not increment Calls. Thus charged Calls<=charged Steps on supported trusted SemCode routes. The smaller fixed-cap alternative (e.g. 2 million) has no established universal compiler-size justification from the available toy/partial workloads. OWNER contract approval remains separate.

### Exact changed files

- `crates/sm-runtime-core/src/lib.rs`
- `crates/smc-cli/src/app.rs`
- `tests/shf_r_execution_envelope.rs`
- `tests/golden_snapshots/public_api/sm_runtime_core_lib.txt`
- `docs/spec/cli.md`
- `docs/spec/quotas.md`

No VM implementation, defaults, SemCode revision/opcodes, dependencies, PROMETHEUS, Harness, workflows or security policy changes.

### Trust/resource boundaries

`ExecutionContext::VerifiedLocal`, verifier-first execution and one effective `ExecutionConfig` for admission/execution/metrics remain unchanged. Capability profile selection remains independent. Effect/register/symbol/debug-symbol limits and Frames/StackDepth behavior are unchanged. `run-smc` gains no controls. Explicit local configuration is not external-caller authentication. Larger Calls grants no aggregate heap or wall-clock limit.

### Original frozen WSL workload A/B

Actual Ubuntu 24.04 WSL2, Rust 1.97.1, matched release settings, original frozen `lex_calls_32000.sm` and input (31992 bytes), 120s timeout. Existing main binary matched the saved provenance SHA256.

| | A(main, raised Steps only) | B(P3, explicit Calls1000000) |
|---|---:|---:|
| Exit/outcome |1 / quota_exceeded|0 / ok|
| Steps |559809|1093082|
| Charged Calls |16384|31992|
| Peak frames |2|2|
| Effect calls |1|1|
| Effective Steps |200000000|200000000|
| Effective Calls |16384|1000000|
| Frames/StackDepth/Effects limits |256/256/1024|256/256/1024|
| CLI end-to-end ms(single observation) |323.221|580.067|

A reports `Calls limit=16384 used=16385`. B completes the original assertion `digits==5332`; an independent input byte count agrees. A terminates early, so these times are NOT a speedup comparison or VM-only timing.

Source SHA256: `e52cb563a561599ae4bc6a7c123f263f8bab57c1065e635f92e7d2dad96dd820`
Input SHA256: `206d78291eecc6e0a6a343b057f91d0cf84c79e59be92a86dae5440fdfd38c4a`
Standalone O0 SemCode SHA256(both compilers): `7bc3280422e32292c8b0da64728a1ffaa28d9f4b43076a03d0194928604a6e3f`.
Both standalone artifacts verify; application runs independently compile/admit their source at O0. No private VM instrumentation/bypass was used.

### Local qualification

- RED: new exact-boundary test fails against baseline CLI with unknown `--max-calls`(test exit 101).
- Envelope integration 25/25 PASS; all original 20 tests retained and 5 P3 tests added.
- Runtime-core 17/17 PASS(Windows); no-std runtime-core check PASS.
- Public API contracts 89/89 PASS without snapshot-update mode.
- WSL runtime-core/VM/verifier/CLI 684 passed, 0 failed, 1 existing ignored scaling benchmark.
- Invalid SemCode control: baseline/P3 both exit 1 with identical `UnsupportedVersion`; raised-Calls register-budget admission test and capability-denial test PASS.
- Windows-safe workspace format and local staged Harness PASS.
- Local immutable BASE checker against BASE/HEAD PASS. Initial checkout invocation correctly failed provenance because Windows CRLF differs from BASE LF blob; exact BASE blob was executed externally without changing the repository checker. This is not yet hosted proof.
- Two fresh-context adversarial local reviews (accounting and full diff/API compatibility): no findings. These are distinct from hosted CI.

- Windows Admission Guard FullPreflight PASS: workspace tests 5483 passed, 0 failed, 14 existing ignored; workspace all-target check and Clippy with warnings denied; 37-package format check; public API 89/89; temporary BASE integration and no-std checks passed.
- Separate fast 7hell gate PASS (all five fast-gate stages). Hosted CI results are recorded below.
Draft status must remain until independent OWNER review.

### Limitations and stop boundary

200 million is configuration-boundary tested, not a completed 200 million-Calls stress run. No aggregate memory/time guarantee, production authentication claim, self-hosting completion or P4 support is asserted. No P2 regression fix is bundled. Research PRs #2041/#2042/#2046 are untouched.

Do not mark Ready, merge, release/tag, close issues, or start P4/VM optimization under this candidate authorization.



## Local evidence and integrity

All task artifacts are outside tracked paths in C:\Users\OWNER_USER\Documents\Codex\SHF-P3-20261016.
- full-preflight.json/log and windows-workspace-totals.json: FullPreflight PASS, workspace 5483 passed, 0 failed, 14 existing ignored.
- 7hell.json/log: separate fast gate exit 0, all five stages PASS.
- AB.json, baseline-provenance.json, oracle-check.json: original frozen WSL A/B and independent result oracle.
- frozen-integrity.json: all 54 frozen input hashes preserved in both native WSL and Windows mirror.
- relevant-packages.json/log, relevant-test-totals.json: 684 passed, 0 failed, 1 existing ignored.
- api-check.json/log: 89 public API checks passed without update mode.
- harness-base-exact.log: immutable BASE-side local scope PASS for the six-file committed diff.
- harness-trusted-local.log and harness-provenance.json preserve the initial CRLF provenance rejection; no checker was modified to bypass it.
- red-existing-binary.json/log: actual baseline test exit 101; the earlier shell-wrapper exit-code capture error is not used as RED evidence.
- accounting-review.md: independent accounting review; full diff/API review also completed without findings.
- pr-2049.json: live PR identity/check snapshot, refreshed at handoff.

The original active checkout retains HEAD 966816345cd3702b8cc40969b4e8b35e1bf1d17f and its original untracked .codex-remote-attachments/ directory. Own candidate tree is clean. No main push, merge, release, tag, research PR change or P4 work was performed.

## Hosted qualification

Trusted Harness run 38816948192 completed SUCCESS on pull_request_target, with non-skipped trusted-scope job 116703911834. Saved log explicitly binds base 188dec7eddfafaab5926af2d30f528bfe3d89a2c and head 64ca9087c83bf7ac504899246c1e7c8b06062d0f, then PASS mode=trusted-pr.
The aggregate CodeQL check is NEUTRAL with a warning that the default-setup Rust configuration from main was not found for alert comparison. This is retained as an evidence limitation, not represented as PASS. Individual Analyze jobs and Clippy/CI conclusions are reported separately. No scanning settings were changed.

### Hosted qualification snapshot

On exact HEAD `64ca9087c83bf7ac504899246c1e7c8b06062d0f`:
- [PR CI](https://github.com/skulmakov-oss/Semantic/actions/runs/38816948266): SUCCESS.
- [Push CI](https://github.com/skulmakov-oss/Semantic/actions/runs/38816940483): SUCCESS.
- [Trusted Harness trusted-scope](https://github.com/skulmakov-oss/Semantic/actions/runs/38816948192/job/116703911834): SUCCESS, non-skipped pull_request_target; log confirms exact BASE/HEAD and BASE-side decision.
- [Clippy SARIF](https://github.com/skulmakov-oss/Semantic/actions/runs/38816948151): SUCCESS.
- CodeQL Analyze (actions) and Analyze (python): SUCCESS; [Analyze (rust)](https://github.com/skulmakov-oss/Semantic/actions/runs/38816945931/job/116703910126): IN_PROGRESS at handoff.
- Aggregate CodeQL: NEUTRAL, warning that one main default-setup Rust configuration was not found for alert comparison. This is not represented as PASS; no scanning settings were changed.

At snapshot: 23 SUCCESS, 1 NEUTRAL, 1 IN_PROGRESS. No failed checks. Full hosted all-checks-green qualification is not claimed while Rust analysis is pending.

