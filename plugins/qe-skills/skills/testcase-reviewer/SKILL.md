---
name: testcase-reviewer
description: Review test cases or automated tests like a senior test architect. Scores each test on requirement fidelity, oracle correctness, assertion depth, negative and edge coverage, independence from the implementation, determinism and clarity, with evidence and a concrete fix. Finds tests that pass while the product is wrong. Use when the user asks to review tests, "are these tests any good?", or to check AI-written tests before a merge.
argument-hint: "[test files, test folder or test case document]"
---

# testcase-reviewer

A test is good when it fails on wrong behavior. Green tests, coverage and many assertions do not prove this. This skill looks for the reasons why a test could pass while the product is wrong.

## Input

The tests are in `$ARGUMENTS`: test files, a test folder, or a document with manual test cases. If it is empty, ask the user. Also find the requirement or the documented behavior for each test. Without it, review against the test name and the comments, and say so.

## Steps

1. **Map** each test to the behavior or the requirement that it checks.
2. **Score** each test with [the review rubric](references/review-rubric.md): dimensions T1 to T7, 0 to 4 each, with evidence (file and line) for each score below 4.
3. **Find the common weak patterns:**
   - checks only "not null", "not empty", a type, a count, or a status code
   - the expected value comes from the code under test (the same function, formula or mapper), or from a snapshot of the current output
   - the unit under test is mocked, or the test checks only that a mock was called
   - no negative or boundary case for a rule with a limit
   - assertions in a loop or in a condition that can run zero times
   - caught exceptions, early returns, disabled or skipped tests
   - fixed sleeps, the real clock, random data without a seed, shared data between tests, order dependence
   - one test checks many behaviors; the name does not match the checks
4. **Group gaps** for each requirement: which positive, negative, boundary and error cases are missing.
5. **Verdict** for each test: accept, revise or reject (rules in the rubric).

## Output

```
## Test review: <scope>

Tests: <n> | accept <a> | revise <r> | reject <x>

| Test | T1 | T2 | T3 | T4 | T5 | T6 | T7 | Verdict | Main problem | Fix |
|---|---|---|---|---|---|---|---|---|---|---|

### Missing cases by requirement
- R1: no boundary case at the limit 100

### Top 5 fixes
1. ...
```

## Rules

- Judge against the requirement, not against the implementation.
- Each score below 4 has evidence and a concrete fix.
- Do not reward length, comments or nice names. Reward tests that would fail on a wrong implementation.
- If you wrote these tests in this conversation, say so. A separate session gives a more independent review.
- Do not change the tests unless the user asks. To measure strength, offer `mutation-probe`.
