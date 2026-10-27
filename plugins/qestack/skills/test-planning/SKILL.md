---
name: test-planning
description: "Writes a test plan for a sprint, release, epic or feature: scope, risks, approach by level, regression scope, environments, owners and exit criteria. Use when the user says 'test plan' or asks 'what do we test this sprint'. Not for the long-term QA direction (use test-strategy)."
license: Apache-2.0
argument-hint: "[sprint, release, epic or feature]"
---

# test-planning

## Objective

A test plan turns a strategy into work for one scope and one time box. It states what will be tested, how, by whom and when, and how the team knows that it is done. It is short enough to read in five minutes.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use it, and skip the questions that it answers.
2. If it does not exist, find the facts in the repository. Suggest `qa-project-context` once. Do not stop the work for it.
3. Read the test strategy if one exists. The plan must follow it, or say where it differs.

## Discovery questions

1. Which items are in scope (stories, tickets, changes)? Which are out of scope?
2. What is the date, and how much test time is there?
3. Which items are high risk?
4. Which environments and test data are available, and when?
5. Who tests what?

## Workflow

1. **Scope.** List the items with their requirement IDs. Mark new, changed and removed behavior.
2. **Risks.** Score each item by impact and likelihood (see `risk-based-testing`). Name the top risks.
3. **Approach for each item.** The levels (unit, API, integration, contract, UI, exploratory, non-functional), the existing tests to update, and the new tests to add. Use `test-case-designer` for the detailed cases of high-risk items.
4. **Regression scope.** From the changed areas and their reach (see `change-impact`), choose the existing suites to run.
5. **Environments and data.** What each test needs, and when it is ready.
6. **Schedule and owners.** Tasks with an owner and a date. Put the high-risk items first.
7. **Entry criteria.** For example: the build is green, the feature is deployed to the test environment, the test data exists.
8. **Exit criteria.** For example: all high-risk items tested, no open critical or major defects, the regression suites green, the exploratory sessions done, the known risks accepted by the owner.
9. **Risks of the plan itself.** Late delivery, a missing environment, unclear requirements, with a mitigation.

## Output

```
## Test plan: <scope> (<dates>)

| Item | Req IDs | Risk | Levels | New / updated tests | Owner | Status |
|---|---|---|---|---|---|---|

Regression: <suites>   Environments: <...>   Data: <...>
Entry criteria: ...
Exit criteria: ...
Plan risks: ...
```

## Anti-patterns

- **Same depth for every item.** Low-risk items get as much time as high-risk items.
- **No exit criteria.** Testing stops when the time is over, not when the evidence is enough.
- **Regression by habit.** The full suite runs, or nothing runs, without a link to the change.

## Done when

- Each in-scope item has a risk, an approach, tests and an owner.
- The regression scope, environments, data, entry criteria and exit criteria are stated.
- The plan risks have mitigations.

## Related skills

- `risk-based-testing`: scores the items.
- `test-case-designer`: the detailed cases.
- `change-impact`: the regression scope.
- `release-readiness`: checks the exit criteria at the end.
