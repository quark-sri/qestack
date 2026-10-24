---
name: roast-my-code
description: A direct, honest code review with a quality engineering focus. Roasts code, a change or a test suite for testability, hidden bugs, error handling, design smells, readability and missing tests, with a severity and a concrete fix for each point. Use when the user says "roast my code", "be brutal", "tear this apart", or wants a no-nonsense review before a merge.
argument-hint: "[file, folder or change] [mild|medium|savage]"
---

# roast-my-code

The roast is direct, but it is fair and useful. Each point attacks the code, never the person. Each point has evidence and a fix. A joke is allowed only when the point under it is real.

## Input

The target and the tone are in `$ARGUMENTS`. If there is no target, ask the user. The tone is `mild`, `medium` (default) or `savage`. The tone changes only the wording, never the facts.

## Steps

1. **Understand the purpose** of the code from its names, its documentation, its tests and its callers. A roast of code that you do not understand is noise.
2. **Review** the target in this order. Stop a category when you have the five most important points in it.
   1. **Correctness:** bugs and likely bugs (use the questions of `bug-hunter`).
   2. **Testability:** hidden dependencies (clock, random, global state, static calls, network) that make tests hard; long functions with many branches; logic inside constructors or in the UI layer.
   3. **Error handling:** swallowed errors, broad catches, errors turned into success, missing cleanup.
   4. **Design:** duplicated logic, mixed responsibilities, leaky abstractions, magic numbers, primitive types for domain values (money as a float).
   5. **Readability:** misleading names, dead code, commented-out code, deep nesting, comments that say what instead of why.
   6. **Tests:** missing tests for the risky paths, tests that check nothing, tests that copy the logic of the code.
   7. **Security and data:** input that is not validated, secrets in code, personal data in logs.
3. **Rate** each point: `HOT` must fix (bug, security, data loss), `WARM` should fix (risk, cost), `MILD` nice to fix.
4. **Give the fix** for each point: one or two lines, or a small code sketch.
5. **Give credit.** Name what the code does well. An honest roast also shows what to keep.

## Output

```
## Roast: <target> (tone: <tone>)

Verdict in one line: <...>

| # | Heat | Location | Point | Fix |
|---|---|---|---|---|

### What is good
- ...

### If you fix only three things
1. ...
```

## Rules

- Evidence for each point: file and line.
- No point without a fix. No personal remarks. No insults about the author.
- Do not change the code unless the user asks.
- Keep each point short. Put the hottest points first.
