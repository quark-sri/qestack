---
name: mutation-probe
description: Measure test strength by injecting small, realistic faults (mutants) into the code one at a time and running the related tests. A test suite that stays green on a broken rule is weak. Works with or without a mutation testing tool in the project. Use when the user asks "would our tests catch a bug here?", wants to check AI-written tests, or wants a quick mutation score for a function, class or change.
argument-hint: "[file, function or change]"
---

# mutation-probe

Coverage shows that code ran. A mutant shows if a test notices when the code is wrong. This skill changes the code on purpose, one small fault at a time, runs the tests, and always restores the code.

## Input

The target is `$ARGUMENTS`: a function, a class, a file or a change. If it is empty, ask the user. Keep the target small: one function or one class.

## Before you start

1. The working tree must be clean for the target files. If it is not, ask the user to commit or stash first. You must be able to restore each file exactly.
2. Find the command that runs the tests for the target (see `test-runner`). Run it once. All related tests must pass. If they fail, stop: a probe on red tests means nothing.
3. If the project already has a mutation testing tool, offer to run it instead, and report its result in the same format.

## Steps

1. **Choose 5 to 15 mutants** for the target. Each one is small and realistic, and it changes observable behavior. Spread them over the rules of the target:
   - boundary: `<` ↔ `<=`, `>` ↔ `>=`, a limit ± 1
   - logic: negate a condition, `and` ↔ `or`, remove one condition
   - arithmetic: `+` ↔ `-`, `*` ↔ `/`, a wrong rounding mode
   - return: return a constant, the input, null or empty, or the other branch
   - removal: remove a validation, a save call, an event or message, an error throw
   - error: catch and ignore an error, return success on failure
   - Do not make mutants that cannot change behavior, or that only break compilation.
2. **For each mutant, one at a time:**
   1. Apply the change.
   2. Run the related tests.
   3. Record: KILLED (a test failed), SURVIVED (all tests passed), or INVALID (compile error or crash at start).
   4. Restore the file exactly. Check that the file equals the original before you apply the next mutant.
3. **Score** = killed ÷ (killed + survived). Do not count invalid mutants.
4. **For each survivor**, name the missing test: the input and the expected result that would fail on this mutant. Take the expected result from the requirement.

## Output

```
## Mutation probe: <target>

Score: <k>/<k+s> killed (<pct>%) | invalid: <i>

| # | Location | Mutation | Result | Killed by / Missing test |
|---|---|---|---|---|

### Tests to add
1. <input> -> <expected result> (kills M3, M7)
```

## Rules

- Never leave a mutant in the code. Restore after each run, and check the restore at the end with the version control status.
- Do not change the tests during the probe.
- A survivor can be an equivalent mutant (no behavior can show it). Say so only with a reason. A human decides.
- Rough guide: below 60% the tests are weak; 75% or more is good for business rules.
