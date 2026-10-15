# Semantic SHF-R historical research archive

Frozen archive prepared 2026-10-16. **Historical evidence, not current implementation guarantees or a normative specification.** No fixtures are registered as active tests. Do not execute archived scripts blindly: review them and map their placeholder paths to an isolated checkout first.

Source project: [Semantic](https://github.com/skulmakov-oss/Semantic). Comparison main: `188dec7eddfafaab5926af2d30f528bfe3d89a2c`.

## Research index

| Collection | Start here | Status and provenance |
|---|---|---|
| RVM-001 / RVM-002 | [storage evaluation](pr-2041/docs/architecture/map_storage_rvm002_evidence.md), [contract proposal](pr-2041/docs/architecture/map_storage_rvm002_contract_proposal.md) | [PR #2041](https://github.com/skulmakov-oss/Semantic/pull/2041), HEAD `b189c100023295bd3aa4a020d5079ea5beab3a09`. Dual-index MapValue is **superseded**, not authorized production architecture. Canonical single-index AVL was selected separately. |
| Legacy Vec copy elision | [benchmark report](pr-2042/docs/architecture/map_copy_elision_rvm001.md) | [PR #2042](https://github.com/skulmakov-oss/Semantic/pull/2042), HEAD `8db588bea6395839eb543aee453c2b2657e856d5`. Historical baseline-specific optimization, not a proposal to reintroduce Vec storage. |
| E1/E2 design provenance | [original design](pr-2046/docs/architecture/vm_record_field_consumption_design.md) | [PR #2046](https://github.com/skulmakov-oss/Semantic/pull/2046), HEAD `090ad0127c03e7b9c80ed0f3f581de05c1918b6f`. Original design only; current authority is the [main-era document](https://github.com/skulmakov-oss/Semantic/blob/188dec7eddfafaab5926af2d30f528bfe3d89a2c/docs/architecture/vm_record_field_consumption_design.md). No duplicate of that evolved document is imported. |
| WSL Baseline/P1/P2 | [full report](wsl-p1-p2/REPORT.md), [methodology](wsl-p1-p2/METHODOLOGY.md), [summary CSV](wsl-p1-p2/summary.csv) | BASELINE `94c5c50d16c3f2efc7691456755461bedae83b18`; P1 `758738a2edf0e984d6067fb372f003a381723d02`; P2 `188dec7eddfafaab5926af2d30f528bfe3d89a2c`. Original results, failures, INCOMPLETE/INCONCLUSIVE labels retained. |
| P3 bounded Calls | [qualification report](p3-calls/REPORT.md), [raw A/B](p3-calls/AB.json), [oracle](p3-calls/oracle-check.json) | [PR #2049](https://github.com/skulmakov-oss/Semantic/pull/2049), HEAD `64ca9087c83bf7ac504899246c1e7c8b06062d0f`. Historical report's pending-check statements are snapshots, not current CI status. |

Additional local CSV/JSON and small inert research fixtures are in `rvm001-local/`, `rvm002-local/`, `wsl-p1-p2/` and `p3-calls/`. Use [source-map.json](source-map.json) to locate deduplicated payloads; not every original relative path has a physical copy. Original upstream file links and immutable commit IDs are retained there.

## Integrity and download

- [raw-records.zip](raw-records.zip): 1541 unique raw trace/log/time files, 621959 bytes. Download through GitHub's **Raw / Download raw file** control, then verify the hash below. It contains only bulk records; reports and structured datasets stay outside ZIP to avoid duplicating them.
- ZIP SHA-256: `9474b0719f78102c42b547feabce1ea5276318d805d7ed0f099d1014a972c818`.
- [INTEGRITY.json](INTEGRITY.json): SHA-256 and byte count for every public file except itself, plus every ZIP member. The file is anchored by the immutable Git commit.
- [source-map.json](source-map.json): original immutable hashes versus published hashes, exact source identities, deduplication and declared sanitized derivatives.
- [omissions.json](omissions.json): every excluded original file and reason.
- [DISCLOSURE.md](DISCLOSURE.md): disclosure decisions and limitations.
- [VERIFY.md](VERIFY.md) and [verify.py](verify.py): offline verification and reproduction instructions.

The archive retains 5087 source records as 1889 unique evidence payloads, with 3198 duplicate references. 1243 source records required label-only sanitization. Original measurement values are not rewritten.

Historical observations do not establish a zero-overhead, heap, wall-clock, release or self-hosting guarantee. Windows/MSVC and WSL/GNU timings must not be compared as matched-host results. Source compilation, admission, execution and CLI end-to-end timings retain their original classifications.
