# A0–A5 Integration Hypotheses — Single-thread First

This document defines **new research hypotheses**, not claims that A1–A5 were specified in the original A0 ZIP. Each layer must be justified by upstream source and by an explicit correctness invariant.

| Layer | Proposed scope | Single-thread proof obligation |
|---|---|---|
| A0 | Existing thread-local negative cache | Default no-association fast hit; `setLogger` invalidation |
| A1 | Guard arrangement: attempt-first vs guard-first, with original slow fallback | Same Logger pointer for default, custom, reset |
| A2 | Avoid layout/ABI changes if safe manager identity can be established | Same-address manager reconstruction without stale hit |
| A3 | Eliminate redundant work on safe negative hit and avoid repeated thread-ID conversion | Correctness across repeated calls and reset |
| A4 | Safe handling of map lookup and logger lifetime boundaries | Do not dereference map iterator after releasing lock |
| A5 | Final composed path and minimal source patch | One-thread scenario suite passes with every enabled layer |

## Gate sequence

1. A0 experimental source compiles, real BDE component tests pass (evidence exists).
2. Execute a one-thread smoke suite checking each observable transition **against a known Logger identity**: initial global default → install custom → repeated custom lookup → clear custom → repeated default lookup → remove unused logger → reinitialize manager.
3. Do not add additional fast-path state unless its necessity and safe invalidation are proven.
4. Implement and smoke each candidate layer, then compose survivors into A0–A5.
5. **Only after single-thread correctness succeeds for the composed candidate** run modest one-host load.
6. **Only after that** launch a batched multi-runner/multi-thread stress and performance matrix.

## Stop conditions

Incorrect Logger identity, sanitizer violation, unexplained ABI break, unsafe cross-thread invalidation, unsupported TLS portability, or unexpected non-fallback behavior stops the affected design. The legacy slow path is not a correctness oracle if its own concurrent iterator bug is triggered.

The earlier T5 multi-thread result is preliminary evidence for A0 alone, **not** proof of an A0–A5 chain.

## Human authority

All code/tests reside in independent research repository. Research → Staging and Staging → official upstream require separate explicit approval.
