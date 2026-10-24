---
name: test-runner
description: Find out how a project runs its tests, run the right subset (all, one module, one file, one test, by tag, or the tests related to a change), and triage every failure as product bug, test defect, environment problem or flaky test, with evidence. Works for any language and build system. Use when the user asks to run the tests, "why do the tests fail?", or wants a clear test result summary.
argument-hint: "[all | path | test name | tag | changed]"
---

# test-runner

A test run is useful only when each failure has a cause. This skill runs the tests the way the project runs them, and explains each failure.

## Input

The scope is `$ARGUMENTS`: `all`, a path, a test name, a tag or group, or `changed` (the tests related to the current change). If it is empty, ask the user. For a large suite, suggest a smaller scope first.

## Steps

1. **Find the test command.** Look in this order, and use the first one that the project documents:
   1. the project documentation (README, contributing guide, developer docs)
   2. scripts and task files in the repository
   3. the continuous integration configuration (it shows the real commands and the environment)
   4. the build files and the test framework configuration
   Write down the command, how to select a subset, where the reports go, and the services that the tests need (database, queue, containers, environment variables).
2. **Check the environment.** Check that the needed runtime, services and settings exist. If something is missing, tell the user what to start or set. Do not install system software without asking.
3. **Run** the command for the scope. For a long run, run it in the background and wait for it to finish. Keep the full output and the machine-readable report if the framework writes one.
4. **Collect results:** total, passed, failed, errored, skipped, and the time. List the skipped tests with their reason.
5. **Triage each failure.** Read the failure message, the stack trace, the test code and the requirement. Classify:
   - PRODUCT BUG: the test matches the requirement, and the code gives a wrong result
   - TEST DEFECT: the test is wrong (wrong expected value, wrong setup, outdated after an intended change)
   - ENVIRONMENT: a missing service, a port, a credential, a version, the network, disk, memory
   - FLAKY: it passes on a rerun with no change; timing, order or shared data
   - UNKNOWN: not enough evidence; say what you need
6. **Confirm flaky suspects.** Run each failing test again, alone, 2 or 3 times. A test that sometimes passes is flaky. Hand it to `flaky-test-detective`.

## Output

```
## Test run: <scope>

Command: <command>
Result: <passed>/<total> passed | failed <f> | errors <e> | skipped <s> | time <t>

| Test | Triage | Evidence (message, file:line) | Next action |
|---|---|---|---|

### Skipped tests
- <test>: <reason>
```

## Rules

- Do not change a test to make it pass. A failing correct test shows a product bug. That is a good result.
- Do not change production code in this skill, unless the user asks.
- Report the numbers exactly as the run shows them. If the run did not finish, say so.
- For a product bug, offer `bug-report`.
