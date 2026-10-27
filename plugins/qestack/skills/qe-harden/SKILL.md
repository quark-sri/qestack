---
name: qe-harden
description: "Runs the qestack quality loop after implementation: seeds hidden faults, runs the gates, gets an independent judge review, and scores and improves the tests until the bar is met. Use in a qestack repository after the feature is implemented."
license: Apache-2.0
compatibility: "Needs the qestack engine (Python 3.11+), git and a shell. Full guard only in Claude Code."
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-harden

Output: `specs/<feature>/quality-report.md` with the decision ACCEPT or ESCALATE.

## 0. Prepare

1. **Preflight.** Do the preflight of the `qestack` skill. The feature is `$ARGUMENTS`. If it is empty, find it as the preflight says.
2. Run `qestack context --feature <feature>`. Note `loop.max_iterations` and `feature_tag`.
3. Compile the project (`commands.compile`). If it fails, stop: the implementation is not complete.
4. Run the feature tests once: `commands.test_feature`, with `{feature_tag}` replaced by `feature_tag` from the context. For each failing test:
   - test right, code wrong: the implementation is not done. Report it. Ask the user if the code must be fixed first. Code is fixed, never the test.
   - test wrong according to the spec: add an entry to `<runs_dir>/suspected-test-defects.md` and ask the user.
   - not sure: ask the user.

## 1. Hidden faults (once per feature)

1. If `<runs_dir>/faults/` has no `*.patch` files, start `qestack:qe-fault-seeder` (Feature).
2. Start `qestack:qe-test-judge` (Feature, Mode: fault-review). If the verdict in `<runs_dir>/faults/fault-review.json` is `revise`, start the seeder again. At most 2 rounds. If the verdict is still `revise`, continue, and list the open fault findings (counts and requirement IDs only) for the user.
3. Run `git status --porcelain`. No production file may stay changed by the seeder. If a file is still changed, run `qestack fault restore --feature <feature>`.
4. Never tell the test writer about the faults. Do not paste fault details in the conversation.

## 2. Improvement loop (iteration i = 1 to max_iterations)

1. **Gates:** `qestack gate --feature <feature>` (lint, trace, guard, flakiness, mutation, seeded faults). Run it in the background (`run_in_background: true`) and wait for the completion notice. If a command is wrong, stop and tell the user which `[commands]` entry to fix.
2. **Judge:** start `qestack:qe-test-judge` (Feature, Mode: test-review, Iteration: i).
3. **Score:** `qestack score --feature <feature> --iteration i`
   - exit 0 = ACCEPT: go to section 3 (Finish)
   - exit 3 = ESCALATE: go to section 3 (Finish)
   - exit 1 = CONTINUE: continue with step 4
4. **Feedback:** `qestack feedback --feature <feature> --iteration i`
5. **Snapshot:** `qestack snapshot --feature <feature>`
6. **Improve:** start `qestack:qe-test-writer` (Feature, Mode: improve, Phase: harden, Feedback: `<runs_dir>/feedback-i.md`).
7. **Check the writer:** `qestack guard --feature <feature> --source-unchanged`.
   - A VIOLATION means that the writer changed production code or weakened a test.
   - In this loop, a REVIEW `STUB_IN_EXISTING_FILE` is also a violation. The writer may not add stubs after the implementation.
   - Undo a test change with Edit, or ask the user. Ask the user to undo a production change. The hook blocks `git checkout` and `git restore` on locked test files.
8. If `suspected-bugs.md` or `suspected-test-defects.md` has new entries, show them to the user now. Ask whether to fix the code first. Do not continue the loop on a known product bug without the user's decision.
9. Start the next iteration (i + 1) at step 1.

## 3. Finish

1. On ACCEPT: `qestack lock --feature <feature> --phase accepted`.
2. Report to the user (short):
   - the decision and the reason
   - the Test Quality Score and its trend
   - each hard gate with its status and value
   - suspected product bugs (a good result)
   - items for human decision (section 8 of the report)
   - undetected faults: the path `<runs_dir>/faults/undetected.md`. The user reads it. You do not read it or quote it.
   - the audit sample: ask the user to review those tests, record verdicts in `<runs_dir>/human-audit.json`, then use `qe-calibrate`
   - the path of `quality-report.md`

## Rules

- Never weaken tests. Never change thresholds or protected files.
- Do not say that a gate passed if the scorecard says FAIL, NOT_RUN or SKIPPED.
- The writer never reads `seed.json` or any file in `<runs_dir>/faults/` (patches, `catalog.json`, `fault-review.json`, `undetected.md`). The judge in test-review mode reads only `seed-feedback.json`.
- Some faults are held out. They never appear in the feedback. The seed gate uses them to measure the tests without bias. Do not try to find them.
- If a gate cannot run (for example, no mutation tool), report NOT_RUN and tell the user what to install. Do not remove the gate from `required`.
