---
name: test-data-management
description: "Designs test data: builders with valid defaults, unique keys for each test, seeded reference data, synthetic data, masking of personal data and cleanup. Use when the user says 'test data', 'fixtures', 'factories' or 'our tests share data'. Not for environments and containers (use test-environments)."
argument-hint: "[domain objects, test suite or environment]"
---

# test-data-management

## Objective

Shared or hand-made test data is a top cause of flaky and unreadable tests. Good test data is created by each test, is valid by default, shows only the values that matter for the case, and does not contain real personal data. This skill sets up such data.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test data approach, environments and data stores.
2. If it does not exist, find the current approach in the tests (fixtures, factories, seed scripts). Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. How do tests get data today: shared seed data, fixtures, factories, copies of production?
2. Which reference data must exist (countries, currencies, products, roles)?
3. Which data is personal or secret? Which rules apply to it (privacy law, company policy)?
4. Do tests run in parallel, and against shared environments?

## Principles

1. **Each test creates its own data,** with unique keys. It does not depend on data from another test.
2. **Valid by default, explicit for the case.** A builder fills all required fields with valid values. The test sets only the values that matter, so the reader sees them.
3. **Create through the fastest trusted path:** the API for the end-to-end and API tests, the repository or the database for integration tests, plain objects for unit tests.
4. **Reference data is seeded and read-only.** Tests do not change it.
5. **No real personal data.** Use synthetic data. If production data is needed for a migration or a volume test, mask it first, and follow the data policy.
6. **Clean up, or isolate.** Delete what the test created, or use a fresh schema, tenant or namespace.

## Workflow

1. List the domain objects that tests need, with their required fields, rules and relations.
2. Write a builder or factory for each one, with valid defaults and unique keys (a counter or a random value with a fixed seed).
3. Add named variants for the common states ("a paid order", "a locked user").
4. Seed the reference data once for each environment, and make it read-only for tests.
5. Replace shared or fixed data in the existing tests, starting with the flaky ones.
6. Add cleanup or isolation, and run the tests in parallel and in random order to prove it.
7. For volume and performance tests, generate the data with a script and a fixed seed.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **The "golden" shared data set** that all tests change.
- **Fixed IDs and emails** that collide in parallel runs.
- **Copies of production** with real names, emails and payment data.
- **Builders with random values for every field.** Failures do not repeat. Use a seed, and log it.
- **Mystery data:** the test does not show which values matter.

## Done when

- Each domain object in scope has a builder or factory with valid defaults and unique keys.
- Tests create their own data and pass in parallel and in random order.
- Reference data is seeded and not changed by tests.
- No real personal data is in the test data, and any masked data follows the policy.

## Related skills

- `test-environments`: where the data lives.
- `database-testing` and `api-testing`: the paths to create data.
- `flaky-test-detective`: data collisions as a cause of flakiness.
- `edge-case-hunter`: the edge values to add as variants.
