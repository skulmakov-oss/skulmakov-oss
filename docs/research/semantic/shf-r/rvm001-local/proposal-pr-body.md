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
