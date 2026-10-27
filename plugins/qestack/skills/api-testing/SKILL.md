---
name: api-testing
description: "Writes or improves tests for HTTP APIs (REST, GraphQL): status, body, schema, headers, errors, auth, idempotency, pagination and side effects, with any HTTP client. Use when the user says 'API test', 'endpoint test' or 'validate the response schema'. Not for cross-team contracts (use contract-testing)."
license: Apache-2.0
argument-hint: "[endpoint, controller, contract file or API area]"
---

# api-testing

## Objective

A status code alone proves very little. An API test checks the whole contract of one call: the values, the shape, the headers, the errors, who may call it, and what it changes. This skill writes such tests against a real running service (in process or in a test environment), with only third-party services simulated.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its API style, test stack, environments and authentication approach.
2. If it does not exist, find them in the repository (contract files, controllers, existing API tests, configuration). Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Is there a contract (an API description file, a schema, a GraphQL schema)? It is the oracle for shape and errors.
2. How do clients authenticate (token, key, session, mutual TLS)? Which roles and tenants exist?
3. Does the project have an HTTP client library or test helpers for APIs? Use them.
4. Does the API change state (database, messages, calls to other services)? How can the test observe it?

## Principles

1. **Check every effect the contract defines** (see [the API checklist](references/api-checklist.md)): status, body values, shape, headers, error payload, persisted state, side effects, and no side effect on failure.
2. **Validate the shape against the contract** in each test, and check the important values explicitly.
3. **Authorization is a test case.** For each endpoint: no credentials, wrong role, another user's or tenant's object.
4. **Own data in each test.** Create it through the API or a test data helper, and give it unique keys.
5. **Real service, simulated third parties.** Do not mock the API's own database or logic. Simulate only external services that the team does not own.

## Workflow

1. List the endpoints in scope with their contract: inputs, outputs, errors, permissions, side effects.
2. Design the cases for each endpoint (see `test-case-designer`). Include a happy path, each documented error, the authorization cases and the boundaries of each input. Add idempotency, pagination and filters where the contract needs them.
3. Set up the client: base address from configuration, an authentication helper that gets fresh credentials, a request and response log on failure.
4. Write the tests. For each one, check the status, the important values, the shape, the headers that the contract defines, and the state or messages after the call. For a rejected call, check that nothing changed.
5. Run the tests against the target environment with the project's command. Then break one rule on purpose to check that a test fails.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own client, and say so.

## Anti-patterns

- **Status-only tests.** They pass when the body is wrong.
- **Hard-coded tokens.** They expire and differ between environments.
- **Testing against production** with tests that create or delete data.
- **Conditional assertions** (`if` a header exists, check it). The check may never run.
- **Mocking the API's own database.** The test then checks the mock, not the service.

## Done when

- Each endpoint in scope has a happy-path test and a test for each documented error.
- Each endpoint has authorization tests (no credentials, wrong role, another owner's object).
- Each response shape is validated against the contract, and the important values are checked.
- State-changing calls check the stored state or the messages, and rejected calls check that nothing changed.
- The tests run green in the target environment and fail on a deliberate break.

## Related skills

- `contract-testing`: agreements with consumers in other teams.
- `database-testing`: deeper checks of stored state.
- `service-virtualization`: simulate third-party services.
- `security-testing`: injection, authentication and authorization in depth.
