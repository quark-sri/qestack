---
name: mutation-probe
description: "Measure test strength with mutation testing: run the project's mutation tool, or inject small realistic faults by hand one at a time, run the related tests, always restore the code, and report the score, the surviving mutants and the missing test for each survivor. Use when: 'would our tests catch a bug here', 'mutation testing', 'mutation score', 'check if these AI-written tests are strong', 'are our tests checking anything'. Not for: reviewing test style (use testcase-reviewer) or finding untested code (use test-coverage-map). Related: testcase-reviewer, unit-testing, test-coverage-map, test-runner."
argument-hint: "[file, function, class or change]"
---

# mutation-probe

## Objective

Coverage shows that code ran. A mutant shows if a test notices when the code is wrong. This skill changes the code on purpose, one small fault at a time, runs the tests, and always restores the code. Each surviving mutant becomes a concrete missing test.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test commands and any mutation tool.
2. If it does not exist, find the test command and the mutation tool in the build files. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. What is the target? Keep it small: one function, one class, or one change.
2. Does the project have a mutation testing tool? Then use it, with the stack recipe.
3. Are the target files committed? You must be able to restore each file exactly.

## Workflow

1. **Before you start:** the working tree must be clean for the target files. Run the related tests once; they must pass. A probe on red tests means nothing.
2. **With a mutation tool:** run it for the target only (see the stack recipe), read its report, and continue with step 5.
3. **By hand:** choose 5 to 15 mutants spread over the rules of the target:
   - boundary: `<` ↔ `<=`, `>` ↔ `>=`, a limit ± 1
   - logic: negate a condition, swap `and` and `or`, remove one condition
   - arithmetic: `+` ↔ `-`, `*` ↔ `/`, another rounding mode
   - return: a constant, the input, null or empty, the other branch
   - removal: a validation, a save, an event, an error throw
   - error: catch and ignore an error, return success on failure
4. **For each mutant, one at a time:** apply it and run the related tests. Record KILLED, SURVIVED or INVALID (compile error or crash at start). Then restore the file, and check that it equals the original.
5. **Score** = killed ÷ (killed + survived). Do not count invalid mutants.
6. **For each survivor,** name the missing test: the input and the expected result (from the requirement) that would fail on this mutant.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). Without a tool, use the manual workflow.

## Output

```
## Mutation probe: <target>

Score: <k>/<k+s> killed (<pct>%) | invalid: <i> | method: tool <name> or manual

| # | Location | Mutation | Result | Killed by / missing test |
|---|---|---|---|---|

Tests to add: <input> -> <expected result> (kills M3, M7)
```

## Anti-patterns

- **A mutant left in the code.** Restore after each run, and check the version control status at the end.
- **Changing the tests during the probe.**
- **Calling every survivor "equivalent".** Say so only with a reason; a human decides.
- **Mutants that cannot change behavior** or only break the build. They tell nothing.

## Done when

- Each mutant has a result, and the code is restored (the version control status shows no change).
- The score and the method are reported.
- Each survivor has a missing test with an input and an expected result.

## Related skills

- `testcase-reviewer`: why the tests are weak.
- `unit-testing`: write the missing tests.
- `test-coverage-map`: untested code, where every mutant survives.
- `test-runner`: the test commands.
