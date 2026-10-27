---
name: test-case-designer
description: "Designs traceable test cases from requirements with equivalence classes, boundary values, decision tables, state transitions and pairwise, each with an exact expected result and test level. Use when the user says 'design test cases', 'test scenarios for this story' or 'generate tests from this spec'. Not for requirement gaps (use requirement-gaps)."
license: Apache-2.0
argument-hint: "[feature, story or spec]"
---

# test-case-designer

## Objective

A good test case can fail. It has a concrete input, an exact expected result from the requirement, and a reason to exist: the defect that it catches. This skill designs such cases with formal techniques, and puts each case at the cheapest level that can prove it.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test levels, conventions and requirement ID format.
2. If it does not exist, find the test levels in the repository. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Where are the requirements, contracts and data models?
2. Are there open gaps? If yes, run `requirement-gaps` first, or mark the affected cases as blocked.
3. Which format does the team use for test cases: a document, a test management system, comments in code?

## Principles

1. **The requirement is the oracle.** Never take an expected result from the implementation.
2. **Each case catches a named defect.** If no wrong implementation can fail a case, remove it.
3. **The cheapest level wins.** Business rules in unit or API tests. Infrastructure effects in integration tests. Only journeys in end-to-end tests.
4. **Technique follows the rule shape.** See [the design techniques](references/design-techniques.md).

## Workflow

1. **Requirement list** with IDs. Mark each one high, medium or low risk.
2. **Technique** for each requirement. Use more than one technique for high risk.
3. **Cases.** For each case, write:
   - the ID and the covered requirement IDs
   - the category: positive, negative, boundary, error, security, concurrency, idempotency, resilience
   - the setup and data, and the action
   - the expected result: each observable effect, and what must NOT change
   - the source of the expected result
   - "fails when": the defect that it catches
   - the level
4. **Traceability check.** Each requirement has a positive case. Each limit has boundary cases. Each error rule has an error case. List the requirements that do not.
5. **Remove waste.** Merge cases that catch the same defect.

## Output

```
## Test design: <feature>

| Req | Risk | Technique | Test cases | Categories | Gaps |
|---|---|---|---|---|---|

#### TC-001: <short name>
- Covers: R1, AC-2 | Category: boundary | Level: unit
- Setup: ...   Action: ...
- Expected: ... (source: R1 example 2)   Must not change: ...
- Fails when: the limit uses ">" instead of ">="
```

## Anti-patterns

- **"Verify it works".** An expected result that is not an exact value or effect.
- **The expected value from the code.** The test then confirms the bug.
- **Everything end-to-end.** Slow, flaky, and the failure does not point to the cause.
- **Two invalid inputs in one case.** The first error hides the second.

## Done when

- Each requirement has cases from the right technique, with exact expected results and a source.
- Each case names the defect that it catches and its level.
- Requirements without enough cases, and the blocked cases, are listed.

## Related skills

- `requirement-gaps`: before the design.
- `edge-case-hunter`: more edge cases for high-risk rules.
- `unit-testing`, `api-testing`, `ui-automation`: write the tests.
- `testcase-reviewer`: reviews the written tests.
