---
name: qe-judge
description: "Gives an independent qestack verdict on the tagged tests of one feature with the qe-test-judge agent and the rubric, and changes no code. Use in a qestack repository when the user asks if the tests of a feature are correct or trustworthy. Not for a whole untagged suite (use qe-audit)."
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-judge

## Steps

1. **Preflight.** Do the preflight of the `qestack` skill. The feature is `$ARGUMENTS`. If it is empty, find it as the preflight says.
2. **Scope.** The tests in scope carry the feature tag (`qestack context --feature <feature>` shows `feature_tag`). If the tests have no tags, use `qe-audit` instead, or help the user add tags first.
3. **Fresh gate data.** Run `qestack lint --feature <feature>` and `qestack trace --feature <feature>`. If mutation or seeded-fault results are older than the tests, say so: the judge gives better scores with fresh data.
4. **Judge.** Start `qestack:qe-test-judge` (Feature, Mode: test-review, Iteration: n). Use n = the next number after the last entry in `<runs_dir>/history.jsonl`, or 1.
5. **Score.** Run `qestack score --feature <feature> --iteration <n>`. This adds an entry to `history.jsonl`, which a later `qe-harden` run counts. Tell the user.
6. **Report:** verdicts (accept, revise, reject), the most important findings with file and line, suspected product bugs, and the judge gate status. Offer `qe-harden` to fix the findings.

## Rules

- The judge must not be the agent that wrote the tests in this session. If you wrote the tests yourself in this conversation, say so and still use the separate judge agent.
- Do not change tests in this skill.
- For a review from many angles outside the gated workflow (no feature tag, no engine), use the `test-review-panel` skill. It gives findings, not a gate verdict.
