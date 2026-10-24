# Test Judge Rubric (test review)

Version 1.0. The `qe-test-judge` agent uses this rubric. Humans use the same rubric for the audit sample, so that the calibration is fair.

## Stance

- Assume that each test is wrong until the evidence shows that it is correct.
- Judge the test against the **specification**, not against the implementation.
- A test that passes is not evidence. A test that fails on wrong behavior is evidence.
- Use the gate results (lint, trace, mutation survivors, undetected fault areas) as objective input. Do not give a high score that the gate data contradicts.

## Evidence rule

Each score must have evidence: a file and line (`OrderApiTest.java:57` or `OrderApiTest.java:50-64`), or a spec reference (`spec.md#FR-007`). A score without evidence is invalid. The gate tool rejects invalid entries.

## Scale

| Score | Meaning |
|---|---|
| 4 | Strong. No defect found. |
| 3 | Good. Minor issue only. |
| 2 | Weak. A real gap that can hide a defect. |
| 1 | Poor. The test gives little protection. |
| 0 | Broken or misleading. The test can pass when the requirement is not met, or it does not test the requirement at all. |

## Dimensions

### R1. Requirement fidelity

Does the test check the behavior that its requirement IDs state?

- **4:** The test checks exactly the rule in the requirement, including its conditions. The tag IDs are correct.
- **3:** It checks the rule, but one minor condition is implicit.
- **2:** It checks a related behavior, or only part of the rule.
- **1:** The link between the test and the requirement is weak. The ID looks added to pass the trace gate.
- **0:** The test checks something else, or contradicts the requirement.

### R2. Oracle correctness

Where does the expected value come from? Is it correct?

- **4:** The expected values are literals or test data that you can trace to a spec example, a contract or a business rule. They are correct.
- **3:** Correct, but the source is not obvious to a reader (no comment, no TC reference).
- **2:** Some expected values are computed in the test with logic that could share a defect with the code.
- **1:** The expected value comes from the production code (the same method, formula or mapper) or from the current output ("snapshot of what the code returns now").
- **0:** The expected value is wrong according to the spec. (Also log a suspected test defect.)

### R3. Assertion depth

Does the test check all observable effects of the behavior?

- **4:** All effects in the test plan are checked: values, state, events, headers and errors. See the ruleset tables (API, database, Kafka, UI).
- **3:** One minor effect is not checked.
- **2:** An important effect is missing (for example the database state after a create, the event key, or the error code).
- **1:** Only existence, type, status or visibility is checked.
- **0:** No meaningful assertion.

Anchor to gate data: if a surviving mutant is in a method that serves this test's requirement, or `seed-feedback.json` has an UNDETECTED fault with this test's requirement ID and layer, R3 is at most 2 for this test.

Check the category tags too. A test tagged `boundary` uses a value at the limit, or just below or just above it. A test tagged `negative` or `error` checks a rejection. If a tag does not match the test, R1 is at most 2.

### R4. Negative and edge coverage (for the requirement group)

Score the test in the context of the other tests for the same requirement IDs.

- **4:** The group has all negative, boundary and error cases that the test plan lists. This test adds a distinct case.
- **3:** One minor case is missing in the group.
- **2:** An important boundary or error case is missing in the group.
- **1:** The group has only happy-path tests.
- **0:** The test duplicates another test and adds no new case, and the group has gaps.

### R5. Independence

Does the test check the requirement, or does it mirror the implementation?

- **4:** No production logic in the test. Mocks only at the system boundary. The unit under test is real.
- **3:** A small amount of shared helper code with low risk.
- **2:** Heavy mocking of collaborators that hides the real behavior, or partial mirroring.
- **1:** The test mocks the unit under test, or only verifies mock interactions with no outcome check.
- **0:** The test re-implements the production algorithm to get the expected result.

### R6. Determinism and isolation

- **4:** No fixed sleeps, no shared mutable state, no order dependence, own test data, fixed clock and seed.
- **3:** A minor risk (for example a generous timeout without a reason).
- **2:** A real risk: shared data with other tests, time dependence, reliance on external state.
- **1:** Fixed sleeps or order dependence.
- **0:** The flakiness gate reports this test as flaky.

### R7. Clarity

- **4:** The name and display name show the case. Arrange, act and assert are clear. The TC ID is present. One behavior per test.
- **3:** Clear, with a small issue.
- **2:** Hard to see what is checked or why.
- **1:** Several behaviors mixed; misleading name.
- **0:** The name contradicts what the test does.

## Verdict rules (the gate tool applies these and uses the stricter verdict)

1. Any dimension = 0 → **reject**
2. Any dimension = 1 → at least **revise**
3. R1, R2 or R3 < 3 → at least **revise**
4. Average of R1 to R7 < 2.5 → at least **revise**
5. Otherwise → **accept**

## Findings

For each score below 4, write a finding:

```json
{"dimension": "R3", "severity": "major", "evidence": "OrderApiTest.java:57",
 "issue": "Only the status code 201 is checked. The saved order and the OrderCreated event are not checked.",
 "fix": "Assert the response body total=90.00, read the order row by id, and poll for one OrderCreated event with key=orderId."}
```

- `severity`: `critical` (score 0), `major` (score 1–2), `minor` (score 3).
- `fix` must be specific enough for the test writer to act on without asking.

## Suspected product bugs

If a test fails and the test is correct according to the spec, record a suspected product bug. Do not ask the writer to change the oracle.

## Equivalent mutant candidates

If a surviving mutant cannot change any observable behavior, list it as a candidate with a reason. Only a human can accept it.
