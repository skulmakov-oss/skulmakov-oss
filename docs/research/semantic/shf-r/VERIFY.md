# Verification and reproduction

Run `python verify.py` from this directory using Python 3 standard library only. It reads INTEGRITY.json, verifies every listed file and ZIP member, checks CRCs and safe member paths, resolves all source-map destinations, and rejects unlisted public payloads. It does not execute research fixtures, install dependencies, or modify a repository. Hashes authenticate consistency against the manifest; use an immutable Git commit to anchor the manifest itself.

Original hashes are in source-map.json and omissions.json. Byte-identical entries have equal original/public hashes; sanitized derivatives intentionally differ. Historical input/artifact manifests still refer to original bytes; compare them against original_sha256 rather than assuming sanitized filenames or byte identities.

## Reproduction

1. Choose the exact historical source SHA from provenance.json or the WSL report, not branch main.
2. Use a detached isolated checkout, pinned toolchain and a separate release target. Obtain dependencies only with your own approval.
3. Review the archived scripts before use. Map OWNER_USER/WSL_USER and historical paths to local scratch locations; these scripts retain historical assumptions and are not a supported one-command installer.
4. Follow each original methodology, workload, profile, timeout, quotas and admission path. Keep default Calls=16384 for historical P1/P2 comparison; P3's explicit override belongs only to its A/B case. Never bypass verification.
5. Freeze original sources/inputs and compare hashes. Record any intentional path-only derivative separately; do not claim its artifact bytes equal the original without measurement.
6. Retain failures, timeouts, sample variation and INCOMPLETE/INCONCLUSIVE results. Do not recalculate historical tables in place. Add a separately versioned follow-up for new measurements.

The frozen P3 A/B source is the WSL lex_calls_32000 workload, with expected assertion digits=5332. Baseline hits Calls limit=16384 used=16385; the documented candidate run completes with 31992 Calls. This is a historical observed result, not a prospective success promise.

Original source links use immutable Semantic commits. Historical absolute paths are labels, not navigable public URLs. Archive-owned relative links are checked locally; upstream HTTP links are recorded in link-checks.json.
