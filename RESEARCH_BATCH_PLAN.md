# BDE LoggerManager Fast-Path — One-Batch Research Protocol

Status: APPROVED research direction; candidate-specific safety proofs are **not** yet complete. This is NOT upstream sign-off.

## Decision question
Can an optional, correctness-preserving fast path eliminate the default-thread lock/map lookup under custom-logger presence, while keeping all other cases safe and reasonably cheap?

## Candidate pool
- B0 — unmodified upstream baseline.
- A0 — existing negative TLS cache with per-manager identity.
- A1 — guard-first variant; only proven default-thread hits bypass the map.
- A2 — minimal-diff / ABI-neutral design if a validity proof is possible. Reject rather than invent an unsafe pointer-based shortcut.
- A3 — safe-fallback-only baseline variation (fix iterator access while holding lock; no caching) to isolate the benefit of removing an existing iterator hazard.

A1/A2/A3 are hypotheses. Do not present them as implemented or tested until they are.

## Triage design (one Actions batch, not serial human gates)
Stage 0: compile/link and deterministic correctness gates on EACH concrete candidate.
Stage 1: one setup/build per OS/compiler, run broad cases within that environment:
- active custom logger: none / 1 / 10% / 50% / 100% of worker threads;
- worker counts: 1 / 2 / 4 / 8 / 16 / 32 (subject to runner capacity);
- phases: cold start / warm hit / forced miss / frequent setLogger-null/custom transition / manager reconstruction / thread reuse;
- end-to-end: repeated getLogger and representative log-message paths;
- each sample reports ns/op, operations, checksum, trial number, compile flags, CPU, kernel, upstream SHA, candidate SHA.
Stage 2: survivors only: dynamic cross-thread changes, stress, ASan/UBSan/TSan where supported, and compile/platform checks.
Stage 3: survivors only: ABBA/BAAB execution order, multiple fresh runners, median and spread; preserve raw CSV and log URL.

## Invariants & blocking gates
- A fast path may return only when it can PROVE validity; uncertainty must go to original path.
- Never use a dangling map iterator after unlocking.
- The benchmark must check the exact expected Logger identity, not compare two possibly-wrong results.
- Record any ABI layout change and TLS portability explicitly. No ABI claims from successful compilation alone.
- Map writes, setLogger changes, manager destruction/reconstruction, custom logger deallocation must not produce stale cache hits.
- A model PASS is not a real BDE sanitizer PASS.
- Control zero-custom workload and custom-heavy workload are mandatory before a general performance claim.
- Compare end-to-end operations, not only microbenchmarks, before claiming application benefit.
- A skipped/cancelled/failed harness is NOT EXECUTED, not product failure.

## Operational budget
Use one well-designed dispatch per phase; limit per-job runtime and prevent duplicate pushes. Pause expansion when a deterministic harness failure invalidates measurements, then fix the failure class before relaunch. No paid runners.

## Decision / deliverable
Provide side-by-side B0/A0/A1/A2/A3 comparisons where implemented, with exact runs/commits, PASS/FAIL/UNVERIFIED, candidate-specific safety proof, worst-case regressions, and small-diff recommendation. No Research→Staging or upstream PR without fresh human approval.
