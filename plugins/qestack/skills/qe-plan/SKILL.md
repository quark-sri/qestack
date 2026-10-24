---
name: qe-plan
description: Design a spec-first test plan (test-plan.md) for one feature and get an independent plan review. Uses the qe-test-designer and qe-test-judge agents. Use before any test code or implementation exists.
---

# qe-plan

Output: `<feature dir>/test-plan.md`, reviewed and accepted. No test code in this step.

## Steps

1. **Preflight.** `qestack --version` works and `.qestack/project.toml` exists (else use `qe-setup`).
2. **Feature.** Find the feature folder (`specs/<NNN-name>/`). `spec.md` must exist. If `spec.md` contains `[NEEDS CLARIFICATION]`, recommend `qe-grill-spec` first. Continue only if the user agrees; those items become open questions.
3. **Context.** Run `qestack context --feature <feature>`.
4. **Design.** Launch the `qe-test-designer` agent. Give it the feature name and any focus from the user. Wait for its summary.
5. **Plan trace check.** Run `qestack trace --plan-only --feature <feature>`. If it fails, send the missing IDs back to `qe-test-designer`.
6. **Review.** Launch the `qe-test-judge` agent in **plan-review** mode for the feature. It writes `plan-review.json` in the runs folder.
7. **Loop.** If the verdict is `revise` or `reject`, launch `qe-test-designer` again with the path of `plan-review.json`. Tell it to fix every finding. Repeat steps 5 and 6. Stop after 3 review rounds.
8. **Report** to the user:
   - the plan verdict and the number of rounds
   - requirement IDs: total, in the plan, excluded with a reason (the user must confirm each exclusion)
   - test cases by category and by layer
   - open questions (they block the related test cases)
   - next step: `qe-write`

## Rules

- Do not read the implementation. Do not write test code.
- If the review fails after 3 rounds, stop and show the open findings. Do not call the plan approved.
