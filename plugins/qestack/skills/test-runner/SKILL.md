---
name: test-runner
description: "Finds how a project runs its tests, runs the right subset, and triages each failure as product bug, test defect, environment problem or flaky test, with evidence. Use when the user says 'run the tests' or asks 'why do the tests fail'. Not for pipeline design (use ci-cd-integration)."
argument-hint: "[all | path | test name | tag | changed]"
---

# test-runner

## Objective

A test run is useful only when each failure has a cause. This skill runs the tests the way the project runs them, reports the numbers exactly, and explains each failure with evidence.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test commands, environments and report paths.
2. If it does not exist, find the commands as below. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. What is the scope: `all`, a path, a test name, a tag, or `changed`?
2. Which environment and services do the tests need?

## Workflow

1. **Find the test command.** Look in the project documentation, then the scripts and task files, then the pipeline configuration (it shows the real commands and the environment). Then look in the build files and the test framework configuration. Note how to select a subset and where the reports go.
2. **Check the environment:** runtime, services, settings. If something is missing, tell the user what to start or set. Do not install system software without asking.
3. **Run** the command for the scope. For a long run, run it in the background and wait for it. Keep the full output and the machine-readable report.
4. **Collect:** total, passed, failed, errored, skipped, time. List the skipped tests with their reason.
5. **Triage each failure** from the message, the stack trace, the test code and the requirement:
   - PRODUCT BUG: the test matches the requirement; the code gives a wrong result
   - TEST DEFECT: the test is wrong (wrong expected value, wrong setup, outdated after an intended change)
   - ENVIRONMENT: a missing service, port, credential, version, network, disk or memory
   - FLAKY: it passes on a rerun with no change
   - UNKNOWN: say what evidence is needed
6. **Confirm flaky suspects:** run each one alone 2 or 3 times. Hand confirmed ones to `flaky-test-detective`.

## Output

```
## Test run: <scope>

Command: <command>
Result: <passed>/<total> passed | failed <f> | errors <e> | skipped <s> | time <t>

| Test | Triage | Evidence (message, file:line) | Next action |
|---|---|---|---|

Skipped tests: <test> - <reason>
```

## Anti-patterns

- **Changing a test to make it pass.** A correct test that fails shows a product bug.
- **"All tests pass" without a run,** or with numbers from an earlier commit.
- **Rerun until green** and report green.

## Done when

- The command, the environment and the commit are stated.
- The numbers are exactly as the run shows them, including skipped tests.
- Each failure has a triage class and evidence.

## Related skills

- `flaky-test-detective`: the confirmed flaky tests.
- `bug-report`: the product bugs.
- `change-impact`: the tests to run for a change.
- `ci-cd-integration`: the pipeline.
