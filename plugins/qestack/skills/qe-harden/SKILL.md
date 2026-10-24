---
name: qe-harden
description: Post-implementation quality loop. Seeds hidden faults, runs the lint, trace, guard, flakiness, mutation and seeded-fault gates, gets an independent judge review, scores the result and improves the tests until the quality bar is met or a human must decide. Use after the feature is implemented.
---

# qe-harden

Output: `specs/<feature>/quality-report.md` with the decision ACCEPT or ESCALATE.

## 0. Prepare

1. **Preflight.** `qestack --version` works and `.qestack/project.toml` exists.
2. Run `qestack context --feature <feature>`. Note `loop.max_iterations`.
3. Compile the project (`commands.compile`). If it fails, stop: the implementation is not complete.
4. Run the feature tests once (`commands.test_feature`). For each failing test:
   - test right, code wrong: the implementation is not done. Report it. Ask the user if the code must be fixed first. Code is fixed, never the test.
   - not sure: ask the user.

## 1. Hidden faults (once per feature)

1. If `<runs_dir>/faults/` has no `*.patch` files, launch the `qe-fault-seeder` agent for the feature.
2. Launch `qe-test-judge` in **fault-review** mode. If the verdict is `revise`, launch the seeder again with `fault-review.json`. At most 2 rounds.
3. Run `git status --porcelain`. No production file may stay changed by the seeder.
4. Never tell the test writer about the faults. Do not paste fault details in the conversation.

## 2. Improvement loop (iteration i = 1 to max_iterations)

1. **Gates:** `qestack gate --feature <feature>` (lint, trace, guard, flakiness, mutation, seeded faults). Let it finish. If a command is wrong, stop and tell the user which `[commands]` entry to fix.
2. **Judge:** launch `qe-test-judge` in **test-review** mode with the feature and `iteration = i`.
3. **Score:** `qestack score --feature <feature> --iteration i`
   - exit 0 = ACCEPT: go to step 3
   - exit 3 = ESCALATE: go to step 3
   - exit 1 = CONTINUE: continue below
4. **Feedback:** `qestack feedback --feature <feature> --iteration i`
5. **Snapshot:** `qestack snapshot --feature <feature>`
6. **Improve:** launch `qe-test-writer` in **improve mode** with the path `<runs_dir>/feedback-i.md`.
7. **Check the writer:** `qestack guard --feature <feature> --source-unchanged`. A violation means that the writer changed production code or weakened a test. Undo that change before the next iteration.
8. If `suspected-bugs.md` has new entries, show them to the user now. Ask whether to fix the code first. Do not continue the loop on a known product bug without the user's decision.

## 3. Finish

1. On ACCEPT: `qestack lock --feature <feature> --phase accepted`.
2. Report to the user (short):
   - the decision and the reason
   - the Test Quality Score and its trend
   - each hard gate with its status and value
   - suspected product bugs (a good result)
   - items for human decision (section 8 of the report)
   - the audit sample: ask the user to review those tests, record verdicts in `<runs_dir>/human-audit.json`, then use `qe-calibrate`
   - the path of `quality-report.md`

## Rules

- Never weaken tests. Never change thresholds or protected files.
- Do not say that a gate passed if the scorecard says FAIL, NOT_RUN or SKIPPED.
- The writer never sees `seed.json` or the patches. The judge sees only `seed-feedback.json`.
- If a gate cannot run (for example, no mutation tool), report NOT_RUN and tell the user what to install. Do not remove the gate from `required`.
