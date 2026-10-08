# BDE A0 LoggerManager TLS Research

Independent, PUBLIC (not a fork); may be changed to PRIVATE by the repository owner. Upstream `bloomberg/bde` is read-only. **Research only, not an upstream submission.**

## Hypothesis

When one or more threads use custom loggers, default-logger threads repeatedly enter `getLoggerSlow()`, acquire a read lock and check a map. A per-thread *negative* cache skips repeated lookups while deliberately never caching a custom logger pointer.

## Actual source

- `groups/bal/ball/ball_loggermanager.cpp`
- `groups/bal/ball/ball_loggermanager.h`
- Source fingerprint for paired benchmark upstream: `75dcd617380748053bebb30aa6ca73735677e849`
- Experimental source edits are applied by `scripts/apply_a0_to_bde.py` inside Actions; official upstream has not been modified.

## Evidence

| Stage | Exact run | Outcome | Scope |
|---|---|---|---|
| T0 source probe | https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37744629792 | PASS | Source structure only |
| T1 model | https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37746073714 | PASS | Ubuntu/macOS, **not actual BDE** |
| T2 sanitizer model | https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37746182161 | PASS | ASan/UBSan/TSan, **not actual BDE** |
| T3 real BDE build | https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37746803302 | PASS | Experimental A0 source compiles in `ball` target |
| T4 real BDE component tests | https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37747482124 | PASS | Official `ball_loggermanager.t` driver |
| T5 actual BDE paired benchmark | https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37748355872 | PASS | Actual `getLogger()` with one custom association, other threads default |

## T5 baseline / candidate, median across five repeats

| Default worker threads | Baseline ms | A0 ms | Ratio |
|---|---:|---:|---:|
| 1 | 1.49872 | 0.679544 | 2.21x |
| 2 | 15.6194 | 1.33255 | 11.72x |
| 4 | 49.9603 | 1.87281 | 26.68x |
| 8 | 106.75 | 3.77951 | 28.24x |

The benchmark is intentionally targeted and is **not** evidence for whole-application logging throughput. Five repeats on one runner do not establish cross-host generality. No-control / custom-heavy / logging end-to-end / portability regression tests have not been completed.

## Design and red flags

- The upstream implementation unlocks `d_defaultLoggersLock` before using its map iterator. That lifetime hazard is investigated separately; the experimental patch copies the result under lock.
- TLS negative cache is invalidated on `setLogger`; per-manager monotonically increasing identity protects same-address reuse.
- The experimental patch adds a member to `LoggerManager` (possible ABI effect) and uses `std::atomic` / `thread_local` (platform/toolchain portability review required).
- A negative cache is safe only if all operations capable of creating an association for the current thread invalidate that thread's negative state. This invariant needs explicit upstream review.
- These observations are **not** production readiness or permission to submit.

## Publication gate

No Staging or Production mutation without separately explicit contributor approval.
