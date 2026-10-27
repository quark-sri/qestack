---
name: bug-hunter
description: "Hunts real bugs in code, a change or a feature with a defect taxonomy, traces real values and proves each suspect with a failing test or exact repro steps. Use when the user says 'find bugs', 'bug hunt' or asks 'what is wrong with this code'. Not for style review (use roast-my-code)."
license: MIT
argument-hint: "[file, folder, change or feature]"
---

# bug-hunter

## Objective

A bug is a difference between what the code does and what it must do. This skill finds such differences and proves them. A suspicion without proof is a lead, not a bug. The result is a short list of proven bugs, each with a failing test or exact steps.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its risk areas, test commands and conventions.
2. If it does not exist, read the documentation and the tests of the target. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. What is the target? Small targets give better results. For a large target, start with `risk-based-testing` or ask for the most important area.
2. Where is the intent: requirements, a contract, documentation, a ticket?
3. May you add failing tests to prove the bugs?

## Workflow

1. **Learn the intent.** Write in 3 to 5 lines what the code must do. Where no source says it, use common sense, and mark it as an assumption.
2. **Map the code:** entry points, inputs, outputs, side effects, and dependencies that can fail.
3. **Hunt** with [the bug taxonomy](references/bug-taxonomy.md) for each entry point. Trace real values: a normal value, a limit, an empty value, a failure of each dependency. Read the callers too; bugs often sit between two correct-looking functions.
4. **Collect suspects:** location, category, trigger, expected result (with the source), actual result (from the trace), confidence.
5. **Prove** each high and medium suspect: with the user's agreement, write the smallest failing test in the style of the project and run it. It must fail for the predicted reason. Otherwise give exact reproduction steps. If the proof fails, drop the suspect or lower its confidence.
6. **Report** proven bugs first.

## Output

```
## Bug hunt: <target>

Intent: <3-5 lines>
Suspects: <n> | Proven: <p> | Dropped: <d>

| # | Severity | Confidence | Location | Category | Trigger | Expected | Actual | Proof |
|---|---|---|---|---|---|---|---|---|
```

## Anti-patterns

- **Style findings reported as bugs.** They belong to `roast-my-code`.
- **Suspects reported as bugs** without proof.
- **Fixing the code** without being asked. The proven bug and the failing test are the result.
- **Comparing with the current behavior** instead of the intent.

## Done when

- Each entry point was checked against the taxonomy with real values.
- Each reported bug has a failing test or exact steps, a severity and the source of the expected result.
- Unproven suspects are listed as leads, with their confidence.

## Related skills

- `bug-report`: the defect report for each proven bug.
- `roast-my-code`: design and readability feedback.
- `edge-case-hunter`: the inputs to trace.
- `security-testing`: security bugs in depth.
