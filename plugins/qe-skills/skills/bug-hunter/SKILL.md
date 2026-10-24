---
name: bug-hunter
description: Hunt for real bugs in code, a change, a module or a feature. Reads the code against its requirements with a defect taxonomy (logic, boundaries, null and empty, errors, state, concurrency, data, security, integration, time), ranks suspects by evidence, and proves each one with a failing test or exact reproduction steps. Use when the user asks to find bugs, "what is wrong with this code?", to review a risky change, or to investigate a reported defect.
argument-hint: "[file, folder, change or feature]"
---

# bug-hunter

A bug is a difference between what the code does and what it must do. This skill finds such differences and proves them. A suspicion without proof is a lead, not a bug.

## Input

The target is `$ARGUMENTS`: files, a folder, a change (a branch or a commit range), or a feature. If it is empty, ask the user. Small targets give better results. For a large target, start with `risk-map` or ask the user for the most important area.

## Steps

1. **Learn the intent.** Read the requirements, the contract, the documentation, the comments and the tests of the target. Write down in 3 to 5 lines what the code must do. Where no source says it, use common sense, and mark it as an assumption.
2. **Map the code.** List the entry points, the inputs, the outputs, the side effects, and the dependencies that can fail.
3. **Hunt.** Go through [the bug taxonomy](references/bug-taxonomy.md) for each entry point. Trace real values through the code: a normal value, a limit value, an empty value, a failure of each dependency. Read the callers too. A bug often sits between two correct-looking functions.
4. **Collect suspects.** For each suspect, write:
   - location (file and line)
   - category from the taxonomy
   - the input or the sequence of events that triggers it
   - expected result (with the source) and actual result (from reading the code)
   - confidence: high (the trace is clear), medium, low
5. **Prove.** For each high and medium suspect:
   - If the user agrees, write the smallest failing test that shows the bug, in the style of the existing tests, and run it. The test must fail for the reason that you predicted. Do not change production code.
   - Otherwise, give exact reproduction steps.
   - If the proof fails, say so, and lower the confidence or drop the suspect.
6. **Report** in the format below, proven bugs first.

## Output

```
## Bug hunt: <target>

Intent: <3-5 lines>
Suspects: <n> | Proven: <p> | Dropped: <d>

| # | Severity | Confidence | Location | Category | Trigger | Expected | Actual | Proof |
|---|---|---|---|---|---|---|---|---|

### Details for each proven bug
#### B1: <title>
- Trigger: ...
- Expected (source): ...
- Actual: ...
- Proof: <test name and its failure message, or the reproduction steps>
- Suggested fix direction: <one line; do not change the code>
```

## Rules

- Compare with the intent, not with your preferred style. Style findings belong to `roast-my-code`.
- Do not fix the code unless the user asks. A proven bug and a failing test are the result.
- Do not report a suspect as a bug before you have proof. Label it as a lead.
- Severity: critical (data loss, security, money, crash of a main path), major (wrong result for a common case), minor (rare case, workaround exists).
- For a proven bug, offer `bug-report` to write the defect report.
