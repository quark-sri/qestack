---
name: mutation-probe
description: "Measure test strength with mutation testing: run the project's mutation tool, or apply small realistic faults one at a time in an isolated copy of the code (by hand or from a fault plan), run the related tests, never leave a fault in the working code, and report the score, the surviving mutants and the missing test for each survivor. Use when: 'would our tests catch a bug here', 'mutation testing', 'mutation score', 'check if these AI-written tests are strong', 'are our tests checking anything'. Not for: reviewing test style (use testcase-reviewer) or finding untested code (use test-coverage-map). Related: testcase-reviewer, unit-testing, test-coverage-map, test-runner."
argument-hint: "[file, function, class or change]"
---

# mutation-probe

## Objective

Coverage shows that code ran. A mutant shows if a test notices when the code is wrong. This skill changes a copy of the code on purpose, one small fault at a time, and runs the tests. The working code of the user never contains a fault. Each surviving mutant becomes a concrete missing test.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test commands and any mutation tool.
2. If it does not exist, find the test command and the mutation tool in the build files. Suggest `qa-project-context` once. Do not stop the work for it.
3. If `.qestack/project.toml` exists and the `qestack` command works, the engine already measures the mutation score of a tagged feature: `qestack mutation --feature <feature>`. Use it for a feature with a feature tag. Use this skill for other targets and for fault plans.

## Discovery questions

1. What is the target? Keep it small: one function, one class, or one change.
2. Does the project have a mutation testing tool? Then use it, with the stack recipe.
3. Can you make an isolated copy of the repository, for example a separate version control worktree or a temporary copy? If not, the target files must be committed, so that you can restore each file exactly.
4. Is there a fault plan from a review, for example from `test-review-panel`? Then use its faults as the mutants, and check each prediction.

## Workflow

1. **Before you start:** the working tree must be clean for the target files. Make the isolated copy. Run the related tests once in the copy; they must pass. A probe on red tests means nothing.
2. **With a mutation tool:** run it for the target only (see the stack recipe), read its report, and continue with step 5.
3. **From a fault plan:** take its faults. For each one, check that the `original` line is in the file exactly once. Skip the faults where it is not, and say so.
   **By hand:** choose 5 to 15 mutants spread over the rules of the target:
   - boundary: `<` ↔ `<=`, `>` ↔ `>=`, a limit ± 1
   - logic: negate a condition, swap `and` and `or`, remove one condition
   - arithmetic: `+` ↔ `-`, `*` ↔ `/`, another rounding mode
   - return: a constant, the input, null or empty, the other branch
   - removal: a validation, a save, an event, an error throw
   - error: catch and ignore an error, return success on failure
4. **For each mutant, one at a time, in the copy:** apply it and run the related tests. Record KILLED, SURVIVED or INVALID (compile error or crash at start). Then restore the file in the copy, and check that it equals the original. If no copy is possible, do the same in the working tree, and check the version control status after each mutant.
5. **Score** = killed ÷ (killed + survived). Do not count invalid mutants.
6. **For each survivor,** name the missing test: the input and the expected result (from the requirement) that would fail on this mutant. For a fault plan, mark each prediction as confirmed or wrong.
7. **Clean up:** delete the copy. Check that the working tree of the user has no change.

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

- **Faults in the working code of the user.** Use an isolated copy. A crash in the middle of a run can leave a fault behind. Work in place only when no copy is possible.
- **A mutant left in the code.** Restore after each run, and check the version control status at the end.
- **Changing the tests during the probe.**
- **Calling every survivor "equivalent".** Say so only with a reason; a human decides.
- **Mutants that cannot change behavior** or only break the build. They tell nothing.

## Done when

- Each mutant has a result. The copy is deleted, and the working tree of the user has no change.
- The score and the method are reported.
- Each survivor has a missing test with an input and an expected result.

## Related skills

- `testcase-reviewer`: why the tests are weak.
- `unit-testing`: write the missing tests.
- `test-coverage-map`: untested code, where every mutant survives.
- `test-runner`: the test commands.
