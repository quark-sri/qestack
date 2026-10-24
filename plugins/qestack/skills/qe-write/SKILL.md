---
name: qe-write
description: qestack blind test writing. Writes the feature tests from test-plan.md with the qe-test-writer agent, without the implementation, then passes the lint and trace gates. Use in a qestack repository after qe-plan and before the implementation. Next step is qe-prove.
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-write

Output: executable tests for every test case in `test-plan.md`, written without the implementation, with no hard lint or trace findings.

## Steps

1. **Preflight.** Do the preflight of the `qestack` skill. The feature is `$ARGUMENTS`. If it is empty, find it as the preflight says.
2. **Inputs.** `test-plan.md` must exist. `<runs_dir>/plan-review.json` must have the verdict `accept`. If not, tell the user to run `qe-plan` first and stop. (The user can override. Then say so in the report.)
3. **Snapshot the production code:** `qestack snapshot --feature <feature>`
4. **Write.** Start `qestack:qe-test-writer` (Feature, Mode: write).
5. **Static gates.** Run `qestack lint --feature <feature>` and `qestack trace --feature <feature>`. If either fails, start the writer again in **write mode** with the exact failing lines. At most 3 rounds.
6. **Guard.** Run `qestack guard --feature <feature> --source-unchanged`.
   - A VIOLATION `SOURCE_CHANGED_IN_TEST_PHASE`: the writer changed production code. Tell the user. Ask the user to undo that change.
   - A REVIEW `STUB_IN_EXISTING_FILE`: the writer added a stub to an existing file. Show the file to the user. The user checks that the change only adds stub members.
7. **Report** to the user: tests written by category and layer, lint and trace results, stubs created, guard items. Next step: `qe-prove`.

## Rules

- Report the gate results exactly as the engine prints them.
- The writer must not read the implementation. If the implementation already exists (brownfield), tell the user that the red check in `qe-prove` may need human exemptions.
