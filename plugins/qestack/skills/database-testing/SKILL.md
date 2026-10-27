---
name: database-testing
description: "Tests persistence against a real database engine: mappings, constraints, transactions, concurrency, queries, precision, time zones and migrations with existing data. Use when the user says 'database test', 'repository test' or 'test this migration'. Not for creating test data sets (use test-data-management)."
license: Apache-2.0
argument-hint: "[repository, query, migration or data flow]"
---

# database-testing

## Objective

Many serious defects live between the code and the database: a wrong mapping, a missing transaction, a lost update, a migration that fails on real data. These defects hide behind mocks and in-memory databases. This skill tests them against the same database engine as production, with data that each test owns.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its database, migration tool, environments and test data approach.
2. If it does not exist, find them in the build files, the configuration and the migration folder. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which database engine and version run in production? Can tests start the same engine (a container or a dedicated schema)?
2. How is the schema created: migrations, generated from the model, a script?
3. Which operations must be atomic? Which ones can run at the same time?
4. Which columns hold money, time, or text in other languages?

## Principles

1. **Same engine as production.** Another dialect hides defects in queries, types, constraints and locking.
2. **Read back through another path.** If the test reads with the same method that wrote, a mapping error stays hidden. Use a direct query, or clear the session cache first.
3. **Commit for real when commit matters.** A test transaction that rolls back never sees commit-time constraints, triggers or after-commit actions.
4. **Own data, unique keys.** Each test creates its rows with unique business keys, or each test class gets a clean schema.
5. **Migrations are code.** Test them on a database with existing data, not only on an empty one.

## Workflow

1. List the operations in scope and their rules: what is stored, which constraints apply, what is atomic, what may run at the same time.
2. Start the database engine for tests (see the stack recipe) and apply the migrations.
3. For each operation, write tests from [the database checklist](references/db-checklist.md). Cover the round trip of all fields, constraint violations and rollback on a later failure. Also cover updates of only the intended columns, and deletes with their effect on related rows.
4. Add concurrency tests for operations that may run at the same time: two updates of one row, two inserts that both pass a uniqueness check in code.
5. For each new migration: load data in the old shape, run the migration, check the new shape and the data, and check that the application still reads old rows.
6. Run the tests and break one rule on purpose to check that a test fails.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **An in-memory database with another dialect** for integration tests.
- **Asserting on the object that the code saved.** It may come from a cache, not from the database.
- **"count > 0" checks.** They pass with wrong values and with duplicates.
- **Tests that depend on row order** without an `ORDER BY`.
- **Shared fixed IDs** between tests. Parallel runs collide.

## Done when

- Each operation in scope has round-trip, constraint and rollback tests on the production engine.
- Concurrent operations have a lost-update or a duplicate test.
- Each new migration is tested with existing data.
- Money, time zone and precision columns have explicit checks.
- The tests run green alone and in parallel, and fail on a deliberate break.

## Related skills

- `test-environments`: database containers and schemas for tests.
- `test-data-management`: builders and data sets.
- `api-testing`: the API on top of the data.
- `messaging-testing`: events that must follow a commit.
