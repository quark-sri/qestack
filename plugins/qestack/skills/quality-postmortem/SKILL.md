---
name: quality-postmortem
description: "Runs a blameless postmortem for an escaped defect: timeline, impact, five whys, why the tests and monitoring missed it, and actions with owners. Use when the user says 'postmortem', 'incident review', 'escaped bug' or asks 'why did our tests miss this'. Not for the defect report itself (use bug-report)."
license: Apache-2.0
argument-hint: "[incident, defect or release]"
---

# quality-postmortem

## Objective

An escaped defect shows a gap in the quality system, not only a bug in the code. This skill finds why each safety net missed it, and turns that into actions that stop the whole class of defect, not only this one.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test levels, pipeline and risk areas.
2. If it does not exist, collect the facts from the incident, the change history and the tests. Do not stop the work for the context file.

## Discovery questions

1. What happened, when, and who was affected? How was it found?
2. Which change introduced it, and when?
3. Which tests, reviews and monitors existed for that area?

## Workflow

1. **Timeline:** introduced, deployed, detected, mitigated, fixed. Note the time to detect and to fix.
2. **Impact:** users, money, data, reputation.
3. **Root cause:** ask "why" until you reach a cause in the process or the system, not a person.
4. **Safety net analysis.** The nets are: requirements, design review, unit, API, integration, contract, end-to-end and exploratory tests, code review, pipeline gates and monitoring. For each net, answer: did it exist, did it run, why did it not catch the defect?
5. **Right level:** the cheapest level that could have caught this class of defect.
6. **Actions,** each with an owner and a date:
   - a regression test at the right level that fails without the fix
   - a change to test design or the checklist for this defect class
   - a gate or a monitor where it was missing
   - a requirement or review rule
7. **Follow up:** check later that the actions are done, and that the regression test fails on the old code.

## Output

```
## Quality postmortem: <incident>

Timeline: ...   Impact: ...
Root cause: ...
| Safety net | Existed? | Ran? | Why it missed |
|---|---|---|---|
Right level to catch it: ...
Actions: <action> - owner - date
```

## Anti-patterns

- **Blame.** People act within the system; fix the system.
- **"Add more tests"** as the only action. Name the test, the level and the defect class.
- **Only this bug.** Look for the same pattern elsewhere.
- **Actions without owners or dates.**

## Done when

- The timeline, impact and root cause are stated.
- Each safety net is analyzed.
- Each action has an owner and a date, and the regression test fails on the old code.

## Related skills

- `bug-report`: the defect itself.
- `test-strategy`: when the analysis shows a strategy gap.
- `risk-based-testing`: update the risk scores.
- `test-coverage-map`: find the same gap elsewhere.
