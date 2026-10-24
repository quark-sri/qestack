---
name: test-case-designer
description: Design test cases from requirements with formal test design techniques (equivalence classes, boundary values, decision tables, state transitions, pairwise, error guessing). Produces a traceable test case list with exact expected results and the cheapest test level for each case. Use when the user asks to design, plan or list test cases for a feature, story or API, before or instead of writing test code.
argument-hint: "[feature, story or spec path]"
---

# test-case-designer

A good test case can fail. It has a concrete input, an exact expected result from the requirement, and a reason to exist: the defect that it catches. This skill designs such cases. It does not write test code.

## Input

The requirement source is `$ARGUMENTS`. If it is empty, ask the user. Read the requirements, contracts and data models. Do not read the implementation to choose expected results. If the requirements have gaps, recommend `requirement-gaps` first.

## Steps

1. **Requirement list.** Give each requirement, acceptance criterion and edge case an ID (use the existing IDs).
2. **Risk.** Mark each requirement high, medium or low. High: money, security, data integrity, irreversible actions, external events, legal rules.
3. **Choose the technique** for each requirement. See [the design techniques](references/design-techniques.md). Use more than one technique for a high-risk requirement.
4. **Design the cases.** For each case, write:
   - ID (`TC-001`, ...) and the requirement IDs that it covers
   - category: positive, negative, boundary, error, security, concurrency, idempotency, resilience
   - preconditions and test data (the test creates its own data)
   - action
   - expected result: each observable effect (output, stored state, messages sent, calls made, error code and message), and what must NOT change
   - source of the expected result (requirement ID, example, contract)
   - "Fails when": the defect that this case catches
5. **Choose the level.** Choose the cheapest level that can prove the case: unit, component, API or service, integration (with real infrastructure), end-to-end UI. Put business rules in unit or API tests. Use end-to-end tests only for user journeys.
6. **Traceability check.** Each requirement has at least one positive case. Each requirement with a limit has boundary cases. Each requirement with an error rule has an error case. List the requirements that do not.
7. **Remove waste.** Merge cases that catch the same defect. Remove cases that no wrong implementation could fail.

## Output

```
## Test design: <feature>

### Traceability
| Req | Risk | Technique | Test cases | Categories | Gaps |
|---|---|---|---|---|---|

### Test cases
#### TC-001: <short name>
- Covers: R1, AC-2   | Category: boundary | Level: unit
- Setup: ...
- Action: ...
- Expected: ... (source: R1 example 2)
- Must not change: ...
- Fails when: the limit uses ">" instead of ">="

### Open questions
- ...
```

## Rules

- Expected results are exact values, not "works", "success" or "correct".
- Never compute an expected value with the logic of the code under test.
- One case checks one behavior. A boundary set can be one parameterized case with one expected result for each row.
- Next step for the user: write the tests, then `testcase-reviewer` and `mutation-probe` to check them.
