---
name: risk-map
description: Build a risk map for a product, release, feature or change to decide what to test first and how deep. Scores each area by impact and likelihood of failure, using business impact, code complexity, change frequency, defect history and test gaps. Use when the user asks "what should we test first?", "where are the risks?", needs a test strategy, or has limited time before a release.
argument-hint: "[product area, release, feature or change]"
---

# risk-map

Testing time is limited. Risk-based testing spends it where a failure costs most and is most likely. This skill makes that decision explicit and visible.

## Input

The scope is `$ARGUMENTS`. If it is empty, ask the user: the whole product, one release, one feature, or one change.

## Steps

1. **List the areas.** Split the scope into areas that a user or the business understands: features, user journeys, services, integrations. Use the requirements, the code structure and the documentation.
2. **Impact (1–5)** for each area. Ask: what happens if it fails in production?
   - 5: money is lost, security or privacy is broken, data is lost or wrong, a legal rule is broken, many users are blocked
   - 3: some users get a wrong result, a workaround exists
   - 1: cosmetic, rare, easy to notice and fix
3. **Likelihood (1–5)** for each area. Use the evidence that exists:
   - the code is new or changed a lot recently (history of the version control system)
   - the code is complex: long functions, many branches, much shared state
   - the area had defects before (bug tracker, fix commits, incident notes)
   - many integrations or asynchronous steps
   - the tests are weak or missing (no tests, tests that check little, flaky tests)
   - the requirements are unclear or changed late
4. **Score.** Risk = impact × likelihood. Sort from high to low.
5. **Strategy.** For each area, propose the test depth:
   - 15–25: full design techniques, negative and boundary cases, integration tests, a review of the tests, exploratory testing
   - 8–14: main paths, key boundaries and errors
   - 1–7: smoke checks only
6. **State the evidence.** For each score, write the reason in one line. A score with no reason is a guess. Mark it as a guess.

## Output

```
## Risk map: <scope>

| Area | Impact | Likelihood | Risk | Evidence | Test depth | Current tests |
|---|---|---|---|---|---|---|

### Top risks and actions
1. <area>: <why>. Action: <what to test, at which level>

### Assumptions to confirm
- ...
```

## Rules

- Ask the user or the business owner to confirm the impact scores. Impact is a business decision.
- Use data for likelihood when it exists. Say when a score is a guess.
- Review the map when the scope or the code changes.
