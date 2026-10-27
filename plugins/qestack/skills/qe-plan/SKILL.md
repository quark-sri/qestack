---
name: qe-plan
description: "Writes a spec-first qestack test plan (test-plan.md) for one feature with the qe-test-designer agent, then gets an independent plan review. Use in a qestack repository before any test code or implementation exists."
license: MIT
compatibility: "Needs the qestack engine (Python 3.11+), git and a shell. Full guard only in Claude Code."
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-plan

Output: `<feature dir>/test-plan.md`, reviewed and accepted. No test code in this step.

## Steps

1. **Preflight.** Do the preflight of the `qestack` skill (engine version, `.qestack/project.toml`).
2. **Feature.** The feature is `$ARGUMENTS`. If it is empty, find the folder under `specs/`. If it is not clear, ask the user. `spec.md` must exist. If `spec.md` contains `[NEEDS CLARIFICATION]`, recommend `qe-grill-spec` first. Continue only if the user agrees. Those items become open questions.
3. **Context.** Run `qestack context --feature <feature>`.
4. **Design.** Start `qestack:qe-test-designer` (Feature, any focus from the user). Wait for its summary.
5. **Plan trace check.** Run `qestack trace --plan-only --feature <feature>`. If it fails, start the designer again with the missing IDs.
6. **Review.** Start `qestack:qe-test-judge` (Feature, Mode: plan-review). It writes `<runs_dir>/plan-review.json`.
7. **Loop.** If the verdict is `revise` or `reject`, start the designer again with the path of `plan-review.json`. Tell it to fix every finding. Repeat steps 5 and 6. Stop after 3 review rounds.
8. **Exclusions.** Show the user each row with `n/a - <reason>`. Ask the user to confirm each one now.
9. **Report** to the user:
   - the plan verdict and the number of rounds
   - requirement IDs: total, in the plan, excluded with a reason, and the exclusions that the user did not confirm
   - test cases by category and by layer
   - open questions (they block the related test cases)
   - next step: `qe-write`

## Rules

- Do not read the implementation. Do not write test code.
- If the review fails after 3 rounds, stop and show the open findings. Do not call the plan approved.
