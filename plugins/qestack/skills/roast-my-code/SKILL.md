---
name: roast-my-code
description: "Gives a direct code review with a quality engineering focus: correctness, testability, error handling, design smells and weak tests, each with evidence and a fix, in a mild, medium or savage tone. Use when the user says 'roast my code' or 'be brutal'. Not for proving bugs (use bug-hunter)."
license: MIT
argument-hint: "[file, folder or change] [mild|medium|savage]"
---

# roast-my-code

## Objective

The roast is direct, but fair and useful. Each point attacks the code, never the person. Each point has evidence and a fix. The tone changes only the wording, never the facts.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its conventions and risk areas.
2. If it does not exist, read the code, its tests and its callers. Do not stop the work for the context file.

## Discovery questions

1. What is the target, and what is the tone (`mild`, `medium` by default, `savage`)?
2. Is there a team style guide or architecture rule to respect?

## Workflow

1. **Understand the purpose** from the names, the documentation, the tests and the callers. A roast of code that you do not understand is noise.
2. **Review in this order,** at most five points for each category:
   1. Correctness: likely bugs (the questions of `bug-hunter`).
   2. Testability: hidden dependencies (clock, randomness, global state, static calls, network); long functions with many branches; logic in constructors or the UI layer.
   3. Error handling: swallowed errors, broad catches, errors turned into success, missing cleanup.
   4. Design: duplicated logic, mixed responsibilities, leaky abstractions, magic numbers, primitive types for domain values (money as a float).
   5. Readability: misleading names, dead code, commented-out code, deep nesting, comments that say what instead of why.
   6. Tests: missing tests for the risky paths, tests that check nothing, tests that copy the logic.
   7. Security and data: unvalidated input, secrets in code, personal data in logs.
3. **Rate** each point: `HOT` must fix (bug, security, data loss), `WARM` should fix (risk, cost), `MILD` nice to fix.
4. **Fix** for each point: one or two lines, or a small code sketch.
5. **Credit:** name what the code does well.

## Output

```
## Roast: <target> (tone: <tone>)

Verdict in one line: ...

| # | Heat | Location | Point | Fix |
|---|---|---|---|---|

What is good: ...
If you fix only three things: ...
```

## Anti-patterns

- **Personal remarks** or insults about the author.
- **Points without a fix** or without a file and line.
- **A list of 50 nitpicks.** Keep the points that matter, hottest first.
- **Changing the code** without being asked.

## Done when

- Each point has a heat, a location and a fix.
- The good parts and the top three fixes are named.

## Related skills

- `bug-hunter`: proves the correctness points.
- `testcase-reviewer`: the tests in depth.
- `unit-testing`: tests for the risky paths.
- `security-testing`: the security points in depth.
