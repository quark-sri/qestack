# Test review rubric

Score each dimension from 0 to 4. Give evidence (file and line, or the requirement) for each score below 4.

## T1. Requirement fidelity

- 4: The test checks a stated requirement or documented behavior. Its name and tags match what it checks.
- 2: The link to a requirement is unclear, or the test checks a detail that no requirement states.
- 0: The test checks behavior that contradicts the requirement.

## T2. Oracle correctness

- 4: The expected values are literals or test data that trace to a requirement example, a contract or a rule.
- 2: Some expected values are computed in the test with logic that could share a defect with the code.
- 1: The expected value comes from the production code or from its current output.
- 0: The expected value is wrong according to the requirement.

## T3. Assertion depth

- 4: All observable effects are checked: values, stored state, messages sent, errors, and "nothing changed" on failure.
- 2: An important effect is missing (the stored state, the error code, the message content).
- 1: Only existence, type, count, status or visibility is checked.
- 0: No meaningful assertion.

## T4. Negative and edge coverage (for the group of tests of one requirement)

- 4: The group has the negative, boundary and error cases that the rule needs.
- 2: An important boundary or error case is missing.
- 1: Only the happy path.

## T5. Independence from the implementation

- 4: No production logic in the test. Mocks only at the boundary of the system. The unit under test is real.
- 2: Heavy mocking that hides real behavior.
- 1: The unit under test is mocked, or only mock calls are checked.
- 0: The test re-implements the production algorithm to get the expected result.

## T6. Determinism and isolation

- 4: No fixed sleeps, no shared mutable state, no order dependence, own test data, a fixed clock and a fixed seed.
- 2: A real risk: shared data, time dependence, external state.
- 1: Fixed sleeps or order dependence.
- 0: Known to be flaky.

## T7. Clarity

- 4: The name shows the case. Arrange, act and assert are clear. One behavior per test.
- 2: Hard to see what is checked or why.
- 0: The name contradicts what the test does.

## Verdict rules

1. Any dimension = 0 → reject.
2. Any dimension = 1, or T1, T2 or T3 < 3 → revise.
3. Average below 2.5 → revise.
4. Otherwise → accept.
