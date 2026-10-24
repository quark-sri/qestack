---
name: unit-testing
description: "Write, fix or improve unit tests for business rules, calculations, validation, mapping and state logic: arrange-act-assert, exact oracles, parameterized boundary sets, test doubles only at boundaries, a controlled clock and randomness, fast and isolated tests. Use when: 'write unit tests', 'add tests for this class or function', 'improve these unit tests', 'TDD this', 'mock this dependency'. Not for: HTTP endpoints (use api-testing), real databases (use database-testing) or reviewing a whole suite (use testcase-reviewer). Related: test-case-designer, edge-case-hunter, mutation-probe, testcase-reviewer."
argument-hint: "[class, function or file]"
---

# unit-testing

## Objective

Unit tests are the cheapest place to catch a wrong rule. A good unit test runs in milliseconds, checks one behavior with an exact expected value, and fails when the rule is wrong. This skill writes such tests in the style and with the framework of the project.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test framework, conventions and test commands.
2. If it does not exist, find the framework and the conventions in the build files and the existing tests. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which behavior must the unit have? Where is it specified (requirement, documentation, an existing test, a ticket)?
2. Which test framework, assertion library and test double library does the project use already?
3. Are there test data builders, fixtures or helpers to reuse?

## Principles

1. **Test behavior, not implementation.** Assert on outputs and observable effects, not on private methods or the order of internal calls.
2. **Exact oracles.** Expected values are literals from the requirement or obvious from the input. Never compute them with the logic under test.
3. **One behavior in each test.** Arrange, act, assert. The name says the case and the expected result.
4. **Doubles only at the boundary.** Replace the clock, randomness, the network, the file system and other services. Do not replace the unit under test or simple value objects.
5. **Deterministic.** No real time, no unseeded randomness, no shared mutable state, no order between tests.
6. **Boundaries as data.** Use parameterized tests for boundary sets, with one expected value in each row.

## Workflow

1. Read the requirement and the public interface of the unit. List the rules, the limits and the errors.
2. Design the cases (see `test-case-designer` and `edge-case-hunter` for high-risk rules): positive, boundary (at, below, above each limit), negative, error.
3. Find the existing test file and follow its style. Reuse builders and helpers.
4. Write the tests. Make hidden dependencies controllable (pass a clock, a random source or an interface). If that needs a production change, propose it to the user first.
5. Run only these tests with the project's command for one file or one test. They must pass on correct code.
6. **Prove each test can fail.** Break the rule on purpose (or use `mutation-probe`), check that the test fails, then restore the code.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own framework, and say so.

## Anti-patterns

- **Assertion-free or "not null" tests.** They run code and check nothing.
- **Mocking the unit under test,** or checking only that a mock was called.
- **Copying the formula into the test.** A shared defect then passes.
- **Real time or sleeps.** The test fails at midnight, at month end or on a slow machine.
- **Catch-all in the test.** An exception that the test catches and ignores hides the failure.

## Done when

- Each rule, limit and error of the unit has a test with an exact expected value.
- The tests pass, run fast, and run alone and in any order.
- At least one deliberate break of each important rule makes a test fail.
- The tests follow the project's naming and layout.

## Related skills

- `test-case-designer` and `edge-case-hunter`: the cases.
- `mutation-probe`: checks that the tests catch faults.
- `testcase-reviewer`: reviews the result.
- `api-testing`: for behavior behind an endpoint.
