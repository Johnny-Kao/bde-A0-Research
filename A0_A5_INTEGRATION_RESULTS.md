# Integrated A0–A5 research candidate — evidence and limits

## Source
- Upstream BDE SHA: `75dcd617380748053bebb30aa6ca73735677e849`
- A0: `scripts/apply_a0_to_bde.py`
- A1: `scripts/apply_a1_guard.py`
- A2–A5 conservative integration: `scripts/apply_a2_a5_integrated.py`
- All patches applied only to checked-out source inside independent Research Actions; **not** upstream.

## Actual runs
- A0–A5 single-thread compiled and tested: https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37772779255 — PASS.
- A0–A5 one-host preliminary load: https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37773534876 — PASS.
- One-host matrix: 1/2/4/8/16 worker threads; scenarios 1–4 (custom owner only / mixed / all custom / churn), five repeats each. Logs report `mismatches=0` on tested rows.
- **Scenario 0 (zero custom loggers) is currently SKIPPED by the benchmark and MUST be implemented prior to the full regression matrix.**
- The one-host test is candidate-only; it does **not** establish comparative speedup versus baseline. The earlier 28× figure applies to original A0 and its earlier targeted scenario, **not** this integrated patch.
- A2 presently retains a manager generation member with ABI cost; ABI-neutral redesign is NOT solved.
- A3/A4 mostly preserve existing A0 behavior (TLS negative fast-hit and under-lock pointer extraction). A5 modifies invalidation ordering. This is a composed correctness-oriented candidate, not proof of five independent speedups.

## Gates still required before any upstream submission
1. Baseline/candidate paired perf with zero-custom, custom-heavy, and end-to-end logging workloads.
2. Actual BDE sanitizer/race tests and lifecycle/cross-thread review, including cached-state invalidation.
3. Repeatability on fresh runners and supported OS/compiler coverage.
4. ABI and portability decision plus minimized diff.
5. Owner approval before Research→Staging or official upstream PR.

No multi-runner stress dispatched under the single-thread-first agreement until basic integration tests passed. As of these runs basic single-thread and one-host gates passed; full multi-runner validation is a separate pending gate.
