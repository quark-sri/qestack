# Example: order service (runnable, Maven)

A small plain-Java Maven project (no Spring Boot) with typical weak AI-written tests. Every engine gate runs here with real Maven, Surefire, Failsafe and PIT. Feature `001-order-discount` has three requirements: a 10% discount at 100.00 or more (FR-001), rejection of negative totals with ORD-400 (FR-002), and an OrderDiscounted event with the order ID as the key (FR-003).

`WeakDiscountTest` is green. Each requirement has a test. But most of the tests cannot fail when the product is wrong.

## Run it

You need Java 17 or later, Maven 3.9 or later and the `qestack` engine. From this folder:

```bash
qestack doctor
qestack lint --feature 001
qestack trace --feature 001
qestack flaky --feature 001 --runs 3
qestack mutation --feature 001
qestack seed --feature 001       # after you save faults with 'qestack fault begin' and 'qestack fault save'
qestack score --feature 001
```

The engine finds `.qestack/` in this folder, also when the example is inside a larger git repository.

## Results

Measured on 2026-10-24 with Maven 3.10.0, Surefire and Failsafe 3.6.0, PIT 1.30.1, JUnit 5.14.4 and Java 25.

| Gate | Result | What it shows |
|---|---|---|
| lint | 5 tests: 1 hollow, 1 trivial, 2 shallow, 1 skipped | No test is strong |
| trace | 0 of 6 requirements covered | Only strong tests count for coverage |
| red (on a stub) | 2 of 4 tests pass before the implementation | `discountIsCalculated` (not-null) and `boundaryValues` (empty) cannot fail |
| flaky | 4 tests x 3 random-order runs, 0 flaky | Each run has its own seed |
| mutation | score 47% (7 of 15 killed) | Mutants at the limit, in the discount condition and in the error code survive |
| seed | 1 of 5 faults detected; 0 of 2 held-out faults | The fault details stay in `.qestack/runs/` (not committed), so the test writer never sees them |
| score | TQS 26.8 of 80; decision CONTINUE | The suite needs `/qe-harden` |

Next: run `/qe-harden` with the Claude Code plugin to strengthen the tests (HANDOFF task 4b).
