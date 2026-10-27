---
name: testcase-reviewer
description: "Reviews automated tests or manual test cases like a senior test architect: scores fidelity, oracles, assertion depth, edge cases and determinism, and finds tests that pass on wrong code. Use when the user says 'review my tests', 'test smells' or 'review AI-written tests'. Not for fault injection (use mutation-probe)."
license: MIT
argument-hint: "[test files, test folder or test case document]"
---

# testcase-reviewer

## Objective

A test is good when it fails on wrong behavior. Green tests, coverage and many assertions do not prove this. This skill reviews tests against the requirement, scores them with a rubric, and finds the reasons why a test could pass while the product is wrong.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its conventions, test levels and requirement ID format.
2. If it does not exist, read the existing tests and the documentation. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which tests are in scope? Where are the requirements or the documented behavior for them?
2. Were the tests written by an AI agent or in this conversation? Then say so; an independent session gives a fairer review.

## Workflow

1. **Map** each test to the behavior or requirement that it checks. Without a requirement, review against the test name and the documentation, and say so.
2. **Score** each test with [the review rubric](references/review-rubric.md): T1 to T7, 0 to 4 each, with evidence (file and line) for each score below 4.
3. **Find the weak patterns:**
   - checks only "not null", "not empty", a type, a count or a status code
   - the expected value comes from the code under test, or from a snapshot of the current output
   - the unit under test is mocked, or only a mock call is checked
   - assertions in a loop or a condition that can run zero times
   - caught exceptions, early returns, disabled or skipped tests
   - fixed sleeps, the real clock, unseeded randomness, shared data, order dependence
   - one test checks many behaviors, or the name does not match the checks
4. **Group gaps** for each requirement: the missing positive, negative, boundary and error cases.
5. **Verdict** for each test (rules in the rubric), and the top fixes.

## Output

```
## Test review: <scope>

Tests: <n> | accept <a> | revise <r> | reject <x>

| Test | T1 | T2 | T3 | T4 | T5 | T6 | T7 | Verdict | Main problem | Fix |
|---|---|---|---|---|---|---|---|---|---|---|

Missing cases by requirement: ...
Top 5 fixes: ...
```

## Anti-patterns

- **Rewarding length,** comments or good names instead of the power to fail.
- **Reviewing against the implementation.** The code can be wrong; the requirement is the reference.
- **Scores without evidence.** Each score below 4 needs a file and line and a fix.

## Done when

- Each test in scope has scores T1 to T7, a verdict and evidence for each score below 4.
- Each revise or reject has a concrete fix.
- The missing cases for each requirement are listed.

## Related skills

- `mutation-probe`: measures whether the tests catch faults.
- `test-coverage-map`: the untested areas.
- `unit-testing` and `api-testing`: rewrite the weak tests.
- `test-review-panel`: a deeper review by eight independent personas.
