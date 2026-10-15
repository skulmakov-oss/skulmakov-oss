## SEM-RVM-001 — compatible Map copy elision

OWNER authorized Rust VM optimization and separate storage architecture review. This focused implementation delivers useful compatible improvements while the underlying storage redesign is reviewed separately in #2041.

Base: `94c5c50d16c3f2efc7691456755461bedae83b18`.
Parent: #1910 (remains OPEN). Risk: R3 VM execution.

### Implementation

- MAP_GET / MAP_CONTAINS read the Map register by reference instead of deep-cloning every pair.
- MAP_SET clones surviving pairs once, removes all matching duplicates and appends the new pair.
- Public `Value::Map(Vec<(MapKey, Value)>)`, pair order/PartialEq, source isolation, error/default behavior and SemCode/verifier/capability/quota contracts remain unchanged.
- Focused regression tests and a diagnostic allocator benchmark are included.

### Identical-input measurements

Windows i5-9300H, Rust 1.97.1, release, three alternating process pairs × nine samples = 27 samples per build/case. Generated admitted SemCode inputs were SHA-256 identical. Raw rows and ranges are committed; counting allocator overhead is included, so these are not uninstrumented production speedup promises.

For 100 operations on a 1024-entry Map with 256-byte text values:

| Case | Allocation count before → after | Allocated bytes before → after |
|---|---:|---:|
| GET | 103859 → 1359 | 37278144 → 414144 |
| CONTAINS | 103759 → 1259 | 37252344 → 388344 |
| Insert | 207159 → 104659 | 106023744 → 69159744 |
| Replace | 206959 → 104459 | 84698944 → 47834944 |

Instrumented large-map read timings improve substantially. SET, source-construction and actual SemSeed compiler-pipeline timing ranges overlap/noise: no general end-to-end speedup or regression is established for those cases. SemSeed returns 14 with identical Steps 11785 / Calls 344 / peak Frames 8 / EffectCalls 2. Public clone cost is unchanged.

Lookup remains O(n); persistent SET remains O(n) with deep surviving-value copies; repeated construction remains quadratic. #2041 proposes the separate persistent storage/API migration. This PR is **not** completion of that redesign.

### Qualification

- Focused Map tests: 7 PASS; full sm-vm unit suite: 190 PASS.
- Public API contracts: 89 PASS, no snapshot changes.
- sm-vm all-target Clippy (`-D warnings`): PASS.
- `git diff --check` and staged local Harness: PASS.
- One fresh-context adversarial read-only review: no actionable findings. Not merge authorization.
- Default-profile full workspace all-target tests: PASS (exit 0); Fast 7hell: PASS (all five stages).
- Required R3 FullPreflight: PASS (exit 0), including readiness, temporary merge-preflight and clean tracked worktree. The successful retry used process-local `CARGO_PROFILE_DEV_DEBUG=0`, `CARGO_PROFILE_TEST_DEBUG=0`, `CARGO_INCREMENTAL=0`, `CARGO_BUILD_JOBS=4` and the task-owned target cache. Native Rust debug symbols were omitted; debug assertions, all tests, SemCode debug data and runtime policy were unchanged.
- Environmental limitation preserved: the earlier default-symbol merge-preflight failed with MSVC `LNK1180: insufficient disk space to complete link`. Package-scoped Cargo cleanup removed only this task's root-package debug artifacts (20.9 GiB) before the successful compact retry. No source or other project's artifacts were deleted. An attempted recursive cache-folder delete was rejected by automatic policy and was not executed.
- Hosted CI: all 25 checks SUCCESS on exact HEAD `8db588bea6395839eb543aee453c2b2657e856d5`. Trusted Harness log confirms BASE `94c5c50d16c3f2efc7691456755461bedae83b18`, this exact HEAD and `PASS mode=trusted-pr`: https://github.com/skulmakov-oss/Semantic/actions/runs/38557427004/job/115829926965

No dependencies, language syntax, public payload, SemCode, verifier, capabilities, quota contracts, trusted workflows/checker/envelope, downstream repository or release/tag changed.

**Draft review artifact. No merge without separate OWNER MERGE GO. Public storage breakage remains blocked pending explicit contract review.**


## SEM-RVM-002 — final compatible qualification

Unchanged HEAD: `8db588bea6395839eb543aee453c2b2657e856d5`.
Unchanged BASE/live main: `94c5c50d16c3f2efc7691456755461bedae83b18`.

Final independent read-only review found no actionable production defect. Operand borrowing preserves source/destination overlap safety, validation/error ordering, hit-default laziness, first duplicate GET, all-duplicate removal/replacement-at-end SET and source isolation. Overlap coverage remains static review rather than a newly added opcode matrix; existing benchmark substring-output assertion is a disclosed non-blocking qualification limitation.

Fresh qualification on current source: sm-vm 190 tests PASS; public_api_contracts 89 PASS; full admission_guard FullPreflight PASS (workspace, API, clippy, formatting, readiness, no-default-features and temporary merge preflight); local and exact-base-blob trusted Harness PASS; serialized five-gate 7hell PASS; git diff --check PASS; worktree clean. Process-local compact native debug-symbol settings were used, with no source/config change or skipped test. The first parallel 7hell invocation failed with Windows os error5 removing the task-owned smc.exe; the subsequent serialized run passed, preserving the failure log.

The unchanged matched SEM-RVM-001 release probe binaries were rerun successfully against current unchanged source/artifact identities. This remains compatible copy elimination, not subquadratic storage redesign.

Immediately before Ready transition: all 25 hosted checks SUCCESS, exact head/base verified, auto_merge=null. PR marked Ready for Review under SEM-RVM-002 OWNER GO. It remains OPEN and UNMERGED.

**READY FOR OWNER MERGE REVIEW — NO MERGE AUTHORIZATION.** Separate exact BASE/HEAD OWNER MERGE GO is required. Persistent Map architecture remains separate in #2041 and requires OWNER CONTRACT GO before public payload replacement.