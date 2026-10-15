# Methodology — SHF-R WSL comparison

Read-only source/GitHub experiment. Native Ubuntu-24.04 WSL2 ext4 directory: /home/WSL_USER/shf-r-comparison-20261015.

Exact detached revisions: baseline 94c5c50d16c3f2efc7691456755461bedae83b18; p1 758738a2edf0e984d6067fb372f003a381723d02; p2 188dec7eddfafaab5926af2d30f528bfe3d89a2c.

Original generator extracted verbatim from GitHub Semantic issue #2030 comment 6168428649. Required families retain exact source semantics/inputs. Unrequested tuple_loop is frozen but excluded from mandatory timing matrix. State5/State10 extracted from benchmark_multi_field_state_scaling_sweep at P2, preserving Rust format string output. No substitute MiniLang workload is invented.

Builds: pinned Rust 1.97.1, cargo build --release -p smc-cli --locked --offline; CARGO_NET_OFFLINE=true, CARGO_BUILD_JOBS=2, distinct CARGO_TARGET_DIR. No dependencies installed/downloaded. Each revision retains Cargo manifests/lockfile. Build times are provenance, not benchmark data.

Execution: sequential (no concurrent benchmark/build processes), original application CLI with pure or cli-read-only, trusted-compiler, max_steps=200000000 and metrics=json. OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1 in all cases. Calls remains default 16384. One warm-up (-1), three measured trials (0..2), balanced rotating revision order. Per-run timeout 120 seconds including command startup. Timed-out process group terminated; no timeout extension or success imputation.

External monotonic wall time includes CLI startup, compilation, admission, planning, execution and teardown. Metrics nondeterministic.wall_ms preserves the historical CLI timing method. Neither is VM-only time. GNU time records process peak RSS. Raw output retained per invocation. Load average recorded before every invocation; Windows host contention/thermal/frequency state is uncontrolled and is a residual risk.

Only successful measured samples produce speedups. Range and every unsuccessful sample retained. Scaling uses ordinary least squares log(time) vs log(N) on successful median points; report adjacent slopes/ranges and caveats, not universal asymptotic proof.

Separate CLI compilation/verification timings, if available, are independent command timings, not subtractable phase instrumentation of application mode. VM-only/planner-only time and allocation counts are NOT MEASURED unless an existing supported harness is actually used. O0/O1 run-smc checks retain its original quotas and cannot be represented as trusted-compiler O1 performance qualification.

No installation, tracked edits, GitHub publication, quota changes or implementation. All generated fixtures, artifacts, logs and targets retained outside tracked paths.
