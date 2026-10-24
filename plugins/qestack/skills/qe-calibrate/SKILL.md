---
name: qe-calibrate
description: Measure how far the qestack judge agrees with human reviewers (agreement and Cohen's kappa) from a human audit sample, and propose rubric improvements for the disagreements. Use each sprint, or when the user doubts the judge.
---

# qe-calibrate

The judge is a model. It can be wrong. Calibration shows how much to trust it.

## Steps

1. **Sample.** Open `specs/<feature>/quality-report.md`, section "Human audit sample". It lists 5 random tests and the 5 tests with the lowest judge score.
2. **Human verdicts.** Ask the user to review each test with the rubric (`qestack show rubrics/test-judge`) and to give a verdict: accept, revise or reject. Ask for one test at a time. Do not suggest a verdict first, because that biases the human.
3. **Record.** Write `<runs_dir>/human-audit.json`: `[{"key": "<exact test key>", "verdict": "accept|revise|reject", "note": "..."}]`. Use the exact keys from the report.
4. **Compute.** Run `qestack calibrate --feature <feature>`.
5. **Explain.** Report the agreement and kappa:
   - kappa ≥ 0.7: the judge is reliable for this team
   - 0.6 to 0.7: use the judge with care; review more samples
   - below 0.6: do not trust the judge scores; fix the rubric or the prompt first
6. **Improve.** For each disagreement, find the rubric dimension that caused it. Propose a concrete rubric change (a clearer score anchor or a new example). The rubric file is protected: show the proposal to the user. Do not edit it.

## Rules

- Keep `calibration-history.jsonl` in git. The trend over sprints matters more than one value.
