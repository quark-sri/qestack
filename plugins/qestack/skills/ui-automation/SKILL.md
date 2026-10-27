---
name: ui-automation
description: "Writes, fixes or structures browser end-to-end tests for critical journeys: role, label or test ID locators, auto-waiting assertions, API data setup, page objects, auth reuse and traces. Use when the user says 'UI test', 'end-to-end test' or 'our UI tests are brittle'. Not for business rules (use unit-testing)."
license: Apache-2.0
argument-hint: "[user journey, page or UI test file]"
---

# ui-automation

## Objective

UI tests are the slowest and most fragile tests. They earn their place only for the journeys that must never break, and only when they are stable. This skill writes UI tests that find elements the way a user does, wait for conditions instead of time, and prepare data through faster paths.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its critical journeys, UI test framework, environments and selector conventions.
2. If it does not exist, find the framework and the conventions in the existing UI tests. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which journeys are critical? Which of their rules are already tested at a lower level?
2. Which UI test framework does the project use? Which browsers and devices matter?
3. Do the elements have accessible names or test IDs? Can the team add test IDs?
4. How do tests log in and create data (API, seed scripts, fixtures)?

## Principles

1. **Few, critical journeys.** Test business rules at lower levels. The UI test checks that the journey works end to end.
2. **User-facing locators.** Role and accessible name first, then label or text, then a stable test ID. Never long CSS or XPath paths tied to layout.
3. **Wait for conditions.** Use assertions that retry until the condition is true. Never use fixed sleeps.
4. **Set up through the API, assert through the UI.** Create data and log in through faster paths; check the result that the user sees.
5. **Isolation.** Each test has its own user and data, so tests run in parallel and in any order.
6. **Evidence on failure.** Keep a trace, a screenshot and the console log of each failed test.

## Workflow

1. Write the journey as steps and expected results that a user can see.
2. Prepare the data and the session through the API or fixtures.
3. Write the test with user-facing locators and retrying assertions. Put repeated page logic in a page object or a component helper that has no assertions about the business result.
4. Check each important result that the user sees: a text, a value, a state, a navigation, a message. Also check the stored result through the API when the journey changes data.
5. Run the test several times and in parallel with the others. It must pass every time (see `flaky-test-detective` if not).
6. Break the journey on purpose (for example a wrong value in the API) and check that the test fails with a clear message.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own framework, and say so.

## Anti-patterns

- **Fixed sleeps** and manual polling loops.
- **Layout-bound selectors** (`div:nth-child(3) > span`).
- **Logging in through the UI in every test.** Slow, and a login bug fails every test.
- **Assertions hidden in page objects.** The test no longer shows what it checks.
- **Tests that depend on each other** (test 2 uses the order from test 1).
- **Retries as the fix** for unstable tests.

## Done when

- Each critical journey in scope has one stable test with user-visible checks.
- Locators are user-facing or test IDs; no fixed sleeps.
- Data and sessions are prepared through the API or fixtures; tests run in parallel.
- Failures keep a trace, a screenshot and logs.
- The tests pass in repeated runs and fail on a deliberate break.

## Related skills

- `api-testing`: the rules behind the journey.
- `test-data-management`: data for each test.
- `flaky-test-detective`: unstable UI tests.
- `accessibility-testing`: accessible names also make locators stable.
