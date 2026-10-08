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


## Paired regression evidence — Oct 8, 2026

- https://github.com/Johnny-Kao/bde-A0-Research/actions/runs/37780177198 — PASS both ubuntu-24.04 and ubuntu-22.04. Two hosted runner environments; not independent hardware families.
- Actual BDE, same runner baseline -> candidate, 25 strata per OS × 5 repeats; explicit Logger pointer identities, zero mismatches; unmodified upstream commit shown in the runs. Raw text logs and paired-summary.json uploaded as job artifacts.
- Ubuntu 24.04: 8 workers, one unrelated custom association: 25.987x; 16 workers, same scenario 30.650x; 4 workers mixed with churn 6.274x.
- Ubuntu 22.04: 8 workers, one custom association: 16.896x; 16 workers same scenario 24.206x; 4 workers mixed with churn 3.029x.
- Counterexamples: zero-custom 8 workers ubuntu-24.04 0.929x (regression); all-custom 8 workers ubuntu-24.04 0.978x; single-worker mixed ubuntu-22.04 0.464x. Do NOT present the candidate as unconditionally faster.
- Benchmark case 999's label `scenario=0` was skipped deliberately; a separate true-zero-custom case 996 was added and verified by this paired run.
- Timing is always baseline first and candidate second per host; needs reversed/crossover order with fresh hosts to control thermal/run-order noise.
- A2 ABI-neutral goal is unsolved. A1 and A3 are branch rearrangements with no separately proven net benefit; A4 preserves pointer-under-lock fix. Do not advertise A1–A5 as independent exponential speedups.
- Actual-BDE TSan, sanitizer evidence, cross-platform, real end-to-end logging, and ABI portability remain release blockers. Research Sign-off is NOT approved.
