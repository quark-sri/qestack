---
name: qe-judge
description: Get an independent, evidence-based verdict on a set of tests with the qe-test-judge agent and the qestack rubric. Use when the user asks if tests are correct, deep enough or trustworthy, or wants a second opinion on AI-written tests. Does not change any code.
---

# qe-judge

## Steps

1. **Preflight.** `qestack --version` works and `.qestack/project.toml` exists.
2. **Scope.** Find the feature (`specs/<NNN-name>/`). The tests in scope carry the feature tag (`qestack context` shows `feature_tag`). If the tests have no tags, use `qe-audit` instead, or help the user add tags first.
3. **Fresh gate data.** Run `qestack lint --feature <feature>` and `qestack trace --feature <feature>`. If mutation or seeded-fault results are older than the tests, say so: the judge gives better scores with fresh data.
4. **Judge.** Launch `qe-test-judge` in **test-review** mode. Use `iteration` = the next number in `<runs_dir>/history.jsonl`, or 1.
5. **Score.** Run `qestack score --feature <feature> --iteration <n>`.
6. **Report:** verdicts (accept, revise, reject), the most important findings with file and line, suspected product bugs, and the judge gate status. Offer `qe-harden` to fix the findings.

## Rules

- The judge must not be the agent that wrote the tests in this session. If you wrote the tests yourself in this conversation, say so and still use the separate `qe-test-judge` agent.
- Do not change tests in this skill.
