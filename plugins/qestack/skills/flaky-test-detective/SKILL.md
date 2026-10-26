---
name: flaky-test-detective
description: "Finds the root cause of a flaky test: reproduces it with repeated, random-order, parallel and slowed runs, classifies the cause and fixes the test or reports a product race. Use when the user says 'flaky test', 'intermittent failure', 'fails only in CI' or 'quarantine tests'. Not for a test that always fails (use test-runner)."
argument-hint: "[test name or file]"
---

# flaky-test-detective

## Objective

A retry hides a flaky test; it does not fix it. A flaky test also hides real bugs, because the team stops trusting red. This skill reproduces the flakiness, proves the cause, and fixes the test, or shows that the product has a real race.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test commands, environments and flaky test policy.
2. If it does not exist, find the test command in the repository. Suggest `qa-project-context` once. Do not stop the work for it.
3. If `.qestack/project.toml` exists and the `qestack` command works, `qestack flaky --feature <feature> --runs <n>` runs the tests of a tagged feature many times. Use it to reproduce. Then continue with this workflow to find the cause.

## Discovery questions

1. Which test, and what are the failure messages?
2. How often does it fail, and where (local, pipeline, which agent)?
3. What changed around the time it started?

## Workflow

1. **Read** the test, its setup and cleanup, shared fixtures and helpers, and the code that it calls. Check each item of [the catalog of flaky causes](references/flaky-causes.md). Note the suspects.
2. **Reproduce,** one variation at a time, and record each result:
   - the test alone, 10 to 20 times
   - with its neighbors (the class or file) in random order
   - the full suite as the pipeline runs it (parallel, same order)
   - another time zone and locale
   - a slower machine: limited CPU, many parallel tests
   A failure rate of 1 in 20 needs about 60 runs to show with high confidence. State the number of runs.
3. **Isolate** the smallest failing combination. A failure that needs another test first is an order dependence; find that test.
4. **Prove the cause:** remove it (a fixed clock, own data, a wait for a condition), and run the failing setup again. It must pass every time.
5. **Decide:** a TEST DEFECT (fix the test), or a PRODUCT BUG (a real race or time bug: report it, do not hide it in the test).

## Output

```
## Flaky test: <test>

Symptom: <message, rate, where>
Reproduced: <yes/no>, <how>, <n runs>
Cause: <category> - <one line>
Evidence: <file:line, run results>
Fix: <change>   (test defect | product bug)
Prevention: <rule for the team>
```

## Anti-patterns

- **Retries, longer sleeps or a skip as the fix.** Use them only as a short-term step, with a ticket and an owner.
- **A fixed sleep instead of a wait for a condition.**
- **"Cannot reproduce" without data.** List the ranked suspects and the data to collect next time (logs, seed, order, time).

## Done when

- The flakiness is reproduced with a stated number of runs, or the suspects and the data to collect are listed.
- The cause is proven by a change that makes the failing setup pass every time.
- The fix is a test change or a product bug report, and a prevention rule is stated.

## Related skills

- `test-runner`: the run commands.
- `test-data-management`: data collisions.
- `test-environments`: environment differences.
- `ci-cd-integration`: the flaky test policy.
