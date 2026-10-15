## SEM-RVM-001 — separate architectural OWNER review

OWNER Option 2 authorizes this architectural change proposal. This PR does **not** implement a public `Value::Map` change, alter API snapshots, adopt production dependencies, or authorize merge.

Base: `94c5c50d16c3f2efc7691456755461bedae83b18`.
Parent: #1910 (must remain OPEN).

### Contents

- Contract and migration analysis for `Value::Map(Vec<(MapKey, Value)>)`.
- Isolated Vec / Arc<BTreeMap> / structurally shared B-tree / deterministic HAMT comparison, including replacement order indexing.
- Reproducible prototype source, external-package lock data, 756 raw measurement rows at sizes 16/128/1024.
- Explicit duplicate-import, NaN equality, ordinal exhaustion, library/dependency and integration acceptance gates.

### Evidence and recommendation

Pinned external `im 15.1.0` was used only for evaluation; Semantic manifests and dependencies remain unchanged. Prototype assertions passed for five key families, 100 differential updates, snapshots/order, 128 fully colliding HAMT keys and ordered NaN inequality.

At 1024 entries, retaining 100 updated versions adds about 2.43 MB (Vec), 5.01 MB (Arc<BTreeMap>), 0.83 MB (persistent B-tree) and 0.83 MB (HAMT), above each model's initial/setup live allocation baseline. Single-map storage is larger for persistent models, especially this HAMT. These are requested live allocation bytes, not RSS.

Recommend a structurally shared deterministic ordered tree for contract review. Shared Arc<BTreeMap> still clones the whole tree; deterministic HAMT requires an additional collision/resource argument. Fixed FNV in the probe is **not** a production security recommendation.

Actual VM evidence is supplied by the separate compatible implementation #2042: identical admitted SemCode, compiler-generated construction loops, and the independently authored Semantic SemSeed frontend/checker/interpreter. SemSeed outcome/counters match; its wall-time improvement is INCONCLUSIVE. **The storage prototype has not replaced the VM or demonstrated end-to-end compiler speedup.** Integration measurements are a mandatory later implementation gate, not a completed claim.

### Qualification / limits

- Local Harness: PASS; staged scope is exactly the four proposal/evidence files.
- `git diff --check`: PASS.
- Isolated release prototype: exit 0, assertions completed before interpreting CSV.
- One fresh-context adversarial read-only review: no actionable findings; not merge authorization/full R3 implementation qualification.
- Hosted checks: all 25 SUCCESS on exact HEAD `37a9dd24b55ebc047ffbc79ae58ceb96ee1d9f24`, including Trusted Harness.

No runtime/source/compiler/verifier/workflow/governance file changed. No production dependency, public API break, quota change, downstream modification, release/tag, or merge is included.

**STOP for OWNER contract review before public storage implementation. OWNER retains separate merge authority.**


## SEM-RVM-002 — concrete architecture and actual VM evidence

Latest HEAD: `b189c100023295bd3aa4a020d5079ea5beab3a09`. The earlier SEM-RVM-001 results above remain historical evidence.

- Concrete contract: `docs/architecture/map_storage_rvm002_contract_proposal.md`.
- Actual VM evidence and limitations: `docs/architecture/map_storage_rvm002_evidence.md`.
- Frozen experiment, qualification checks, raw rows, artifact and binary identities: `tests/fixtures/rvm002/`.

Recommended production direction: focused in-tree persistent ordered AVL indexes with Arc storage; no new production dependency. `im-rs` is archived, so its previous research probe is not a production adoption recommendation.

Primary matched reference is exact PR #2042 HEAD `8db588bea6395839eb543aee453c2b2657e856d5`. Both builds execute identical admitted compiler-generated SemCode with equal counters. At 16384 entries: compatible Vec median 30089.401 ms vs persistent VM prototype 171.196 ms, equal Steps 229395. At 32768: persistent primary sample 332.019 ms; compatible reference INCOMPLETE at the 90-second limit. No timeout extension/retry. Three earlier slower large candidate samples are preserved; timing noise and instrumentation are explicit. Full table/raw ranges remain in the evidence document.

Replacement, actual one-version VM snapshots, a 100-version structure memory probe, and actual text/nested-value SemSeed evidence are separated. SemSeed wall-time result remains INCONCLUSIVE; output and Steps/Calls/effects match.

Standalone qualification passes: 10000 Vec-differential updates, five key families, preserved versions, nested NaN, large UTF8 key, AVL/index invariants, synthetic ordinal-limit compaction. These do not substitute for the complete production VM differential matrix.

Independent static architecture and evidence reconciliation found no new actionable contract blocker. Prototype limits are explicit: pathological duplicate import, compaction payload-copy cost, physical Debug, and pending full production API/VM qualification.

**OWNER CONTRACT GO REQUIRED** before production `Value::Map(MapValue)` replacement, exact API snapshot migration and the specified duplicate/order/equality/exhaustion policy. This PR contains proposal/evidence fixtures only; no breaking production payload change, manifest change, verifier/wire/quota-default change or release work.

**NO MERGE AUTHORIZATION.** PR #2042 remains a separate compatible optimization and also requires separate exact BASE/HEAD OWNER MERGE GO.

Hosted checks on exact HEAD b189c100023295bd3aa4a020d5079ea5beab3a09: all 25 SUCCESS at final SEM-RVM-002 handoff. Earlier hygiene failures are historical; the corrected current head is green. PR remains Draft, OPEN and UNMERGED for OWNER CONTRACT REVIEW.

Reproduction-path hygiene correction: hardcoded host paths removed; explicit disposable-clone parameter, exact base identity and tracked-cleanliness guards tested. Local 13 hygiene guard tests and strict scan pass. Earlier failed checks remain historical; current-head CI independently completed with all 25 checks SUCCESS.
