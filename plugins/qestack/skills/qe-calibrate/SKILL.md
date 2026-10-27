---
name: qe-calibrate
description: "Measures how far the qestack judge agrees with human reviewers (agreement and Cohen's kappa) and proposes rubric fixes for the disagreements. Use each sprint, or when the user doubts the judge."
license: Apache-2.0
compatibility: "Needs the qestack engine (Python 3.11+), git and a shell. Full guard only in Claude Code."
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-calibrate

The judge is a model. It can be wrong. Calibration shows how much to trust it.

## Steps

1. **Feature.** The feature is `$ARGUMENTS`. If it is empty, find it as the preflight of the `qestack` skill says.
2. **Sample.** Open `specs/<feature>/quality-report.md`, section "Human audit sample". It lists random tests and the tests with the lowest judge score. Use only the test keys.
3. **Human verdicts.** Ask the user to review each test with the rubric (`qestack show rubrics/test-judge`) and to give a verdict: accept, revise or reject. Ask about one test at a time.
   - Do not suggest a verdict first.
   - Do not show the judge verdict, the judge score or the label "[lowest judge score]" before the human answers. That biases the human.
4. **Record.** Write `<runs_dir>/human-audit.json`: `[{"key": "<exact test key>", "verdict": "accept|revise|reject", "note": "..."}]`. Use the exact keys from the report.
5. **Compute.** Run `qestack calibrate --feature <feature>`. Exit 1 means that kappa is below 0.6, or that an input file is missing.
6. **Explain.** Report the agreement and kappa:
   - kappa ≥ 0.7: the judge is reliable for this team
   - 0.6 to 0.7: use the judge with care; review more samples
   - below 0.6: do not trust the judge scores; fix the rubric or the prompt first
7. **Improve.** For each disagreement, find the rubric dimension that caused it. Propose a concrete rubric change (a clearer score anchor or a new example). The rubric file is protected. Show the proposal to the user. The user can save a project copy in `.qestack/rubrics/test-judge.md`. The agents then use that copy.

## Rules

- Keep `calibration-history.jsonl` in git. The trend over sprints matters more than one value.
