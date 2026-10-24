---
name: qe-write
description: Write the feature tests "blind" from test-plan.md with the qe-test-writer agent, then pass the lint and trace gates. Use after qe-plan and before the implementation. Next step is qe-prove.
---

# qe-write

Output: executable tests for every test case in `test-plan.md`, written without the implementation, with no hard lint or trace findings.

## Steps

1. **Preflight.** `qestack --version` works and `.qestack/project.toml` exists.
2. **Inputs.** `test-plan.md` must exist. `plan-review.json` in the runs folder must have the verdict `accept`. If not, tell the user to run `qe-plan` first and stop. (The user can override. Then say so in the report.)
3. **Snapshot the production code:** `qestack snapshot --feature <feature>`
4. **Write.** Launch the `qe-test-writer` agent in **write mode** with the feature name.
5. **Static gates.** Run `qestack lint --feature <feature>` and `qestack trace --feature <feature>`. If either fails, launch `qe-test-writer` again with the exact failing lines. At most 3 rounds.
6. **Guard.** Run `qestack guard --feature <feature> --source-unchanged`. The only production changes allowed are the stubs in `stubs.json`. If there is a violation, undo that production change and tell the user.
7. **Report** to the user: tests written by category and layer, lint and trace results, stubs created. Next step: `qe-prove`.

## Rules

- Report the gate results exactly as the engine prints them.
- The writer must not read the implementation. If the implementation already exists (brownfield), tell the user that the red check in `qe-prove` may need human exemptions.
