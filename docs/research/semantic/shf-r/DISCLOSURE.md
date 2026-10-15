# Public disclosure and preservation decisions

## Original versus public bytes

Original evidence remains unchanged in OWNER-controlled local storage. Public source labels are collection-relative and contain no personal filesystem prefixes. Each retained source has original SHA-256, published SHA-256, byte counts and a destination in source-map.json. A duplicate reference points to the same content, not to a second copy.

Public derivatives replace the original Windows username with `OWNER_USER`, WSL username with `WSL_USER`, and the hostname label with `ARCHIVE_HOST`. These are explicit label-only changes; sanitized files are not represented as byte-identical originals. JSON numeric values and CSV numeric cells were checked unchanged where sanitization applied. Historical source/input/artifact digest strings are preserved; they describe original bytes, not sanitized descendants. Reproduction involving an affected path requires an explicit local path mapping.

Environment snapshot files, account/API operational dumps, binary build products, the existing unsanitized ZIP and the Git source bundle are not published. A curated host/toolchain description remains in the historical WSL report. No credentials or token values were requested or accessed. Pattern scanning found 0 credential-pattern exclusions among selected text; manual inspection focused on reports, CSV/JSON schemas, source scripts, path fields and package contents. This is a disclosure audit, not a proof that arbitrary historical data can never contain a secret.

## Retained / omitted

262 original records are omitted with per-file hashes and reasons in omissions.json. Generated SemCode binaries can be reproduced from frozen sources and historical commits; their original identities remain available. Old prototype Rust/Python code is inert research evidence, not a production implementation or active test. No caches, targets, object databases or obsolete production diffs are imported.

The local historical source bundle is 22651189 bytes, SHA-256 `b2680ff3f4a3a518ecf6936152e2ae036180904f8af28fda756241e18dfc53be`. Its authoritative logical location is OWNER's SEM-RVM-002/source.bundle; its private absolute location is retained only in the local inventory. It is a repository-history backup rather than necessary numerical evidence and has not undergone a full-history disclosure audit. Do not publish it as an opaque blob. If durable full-history preservation is desired, use an OWNER-controlled encrypted backup with this checksum; any later public copy requires a separate history/secrets audit and OWNER decision. No paid service or release asset was created.

## Original manifest validation

5778 existing hash records were checked. The sole missing Windows export entry was `gen_original.py`; it was recovered read-only from native WSL and exactly matched historical SHA-256 `4e511b001600aabfd26796eadfa76a07ec43ddc8bb0c0cf2a88860ae236988ec`. The Windows export and its manifests were not repaired or rewritten. See original-manifest-validation.json, which preserves the initial mismatch and separate recovery result.

Historical conclusions and measurements are retained even when superseded or unsuccessful. The external archive creates no Semantic Harness authority and changes no quota or runtime contract.
