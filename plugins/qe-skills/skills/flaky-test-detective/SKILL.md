---
name: flaky-test-detective
description: Find the root cause of a flaky test, a test that passes and fails with no code change. Reproduces the flakiness (repeat runs, random order, parallel runs, other time zone or locale, slow resources), classifies the cause (timing, order dependence, shared state, time, randomness, concurrency, environment, external services) and proposes a real fix instead of a retry. Use when the user says a test is flaky, intermittent, "fails only in CI", or "passes on my machine".
argument-hint: "[test name or file]"
---

# flaky-test-detective

A retry hides a flaky test. It does not fix it. A flaky test also hides real bugs: the team stops trusting red. This skill finds the cause and fixes the test, or proves that the product has a real race.

## Input

The test is `$ARGUMENTS`. If it is empty, ask the user. Collect what is known: failure messages, how often it fails, where (local, CI, which agent), and recent changes.

## Steps

1. **Read** the test, its setup and cleanup, its shared fixtures and helpers, and the code that it calls. Check each item in [the catalog of flaky causes](references/flaky-causes.md). Note the suspects.
2. **Reproduce.** Use the test command of the project (see `test-runner`). Try these, one at a time, and record each result:
   - the test alone, 10 to 20 times
   - the test with its neighbors (the whole class or file), in a random order
   - the full suite, as CI runs it (parallel, same order)
   - another time zone and another locale
   - a slower environment: limited CPU, many tests in parallel
   A failure rate of 1 in 20 needs about 60 runs to show with high confidence. Say how many runs you did.
3. **Isolate.** When a combination fails, make it smaller: the fewest tests, the shortest sequence, one setting. A failure that needs another test first is an order dependence. Find that other test.
4. **Prove the cause.** Change one thing that removes the suspected cause (a fixed clock, an own data set, a wait for a condition). The test must pass every time in the setup that failed before.
5. **Decide:** a TEST DEFECT (fix the test) or a PRODUCT BUG (a real race or a time bug in the code: report it, do not hide it in the test).

## Output

```
## Flaky test: <test>

Symptom: <message, rate, where>
Reproduced: <yes/no>, <how>, <n runs>
Cause: <category> - <one line>
Evidence: <file:line, run results>
Fix: <change>   (test defect | product bug)
Prevention: <rule for the team, for example "no shared static state in tests">
```

## Rules

- Do not add retries, longer sleeps or a skip as the fix. Name them only as a short-term step, with a ticket.
- Replace a fixed sleep with a wait for a condition, with a timeout.
- If you cannot reproduce it, say so. List the suspects, ranked, and the data to collect next time (logs, seed, order, time).
