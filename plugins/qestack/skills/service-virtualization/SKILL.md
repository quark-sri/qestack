---
name: service-virtualization
description: "Simulate external and third-party services in tests with stubs, fakes and simulated servers: realistic responses from the contract, error and timeout cases, slow responses, request verification, stateful scenarios, and drift checks against the real service. Use when: 'mock this external API', 'stub the payment provider', 'simulate a downstream service', 'test without the real dependency', 'test timeouts and errors from a dependency'. Not for: replacing the system's own database or logic (use database-testing or api-testing with real components) or agreements between owned services (use contract-testing). Related: api-testing, contract-testing, test-environments, unit-testing."
argument-hint: "[external service or dependency]"
---

# service-virtualization

## Objective

Real third-party services are slow, costly, rate-limited and hard to break on purpose. A simulated service makes tests fast and repeatable, and it can return the errors and delays that the real service shows only in an incident. The risk is a simulation that drifts from reality. This skill builds simulations from the contract and keeps them honest.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its external services and environments.
2. If it does not exist, find the external calls in the code and the configuration. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which external services does the system call? Which of them does the team own?
2. Is there a contract, a sandbox, or recorded traffic for each one?
3. Which failures of the dependency must the system handle: errors, timeouts, slow responses, rate limits, bad data?

## Principles

1. **Simulate only what you do not own** or cannot run in a test. Use the real thing for your own services and data stores.
2. **Responses come from the contract or recorded traffic,** not from what the code under test expects.
3. **Simulate failures on purpose:** error codes, timeouts, slow responses, malformed bodies, rate limits.
4. **Verify the requests** that matter: the system sent the right call with the right data, and did not send it on failure.
5. **Check for drift:** run a small set of checks against the real service or its sandbox on a schedule, and update the simulation when it differs.

## Workflow

1. List the dependencies in scope, with their operations, contract and failure modes.
2. Choose the level of simulation: an in-process fake for unit tests, a simulated HTTP server for API and integration tests, or the provider's sandbox for a few scheduled checks.
3. Build the stubs from the contract: success, each documented error, timeout, slow response, malformed response, rate limit.
4. Point the system to the simulation through configuration (base URL, client settings), not through code changes.
5. In each test, set the stub for the case, run the action, check the system's result, and verify the outgoing request when it matters.
6. Add a scheduled drift check against the real sandbox, if one exists.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **Stubs written from the code's expectations.** They agree with the bug.
- **Only the happy path is simulated.** The error handling is never tested.
- **One global stub set for all tests.** Tests depend on each other's setup.
- **Never checking the real service.** The simulation drifts, and production fails.

## Done when

- Each dependency in scope has stubs for success, each documented error, a timeout and a slow response.
- Tests verify the important outgoing requests and the system's behavior for each failure.
- The simulation is configured, not hard-coded, and each test sets its own stubs.
- A drift check exists, or its absence is stated as a risk.

## Related skills

- `api-testing`: the system's own API under these conditions.
- `contract-testing`: for services that the team owns.
- `test-environments`: where the simulated services run.
- `unit-testing`: in-process fakes.
