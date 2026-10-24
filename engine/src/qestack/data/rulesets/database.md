# Ruleset: Database testing

All agents read this file when `database` is in `[project] rulesets` of `.qestack/project.toml`.

## 1. What a complete database test checks

| Effect | Check |
|---|---|
| Row exists | Query by the business key, not only "count > 0" |
| Column values | Each column that the requirement affects, with exact expected values |
| No extra rows | The operation did not create duplicates |
| Constraints | Unique keys, foreign keys and not-null columns reject bad data |
| Transactions | A failed operation leaves no partial data |
| Soft delete / audit | Status flags, timestamps, audit rows (use a fixed clock) |
| Concurrency | Optimistic locking: the second update with an old version fails |

## 2. Rules

- Read the state with a direct query or a repository call that is NOT the code under test. If the test reads with the same repository method that wrote the data, a mapping error stays hidden.
- Use real database engines for integration tests (Testcontainers or a dedicated test schema). An in-memory database with another SQL dialect can hide defects.
- Isolate data: unique keys for each test, or a clean schema (truncate tables) for each test class.
- Do not use a test-managed transaction that rolls back (for example `@Transactional` on a Spring test) when the test checks commit behavior. Such a test does not see commit-time constraint violations, and after-commit listeners and the outbox do not run. Clean up with truncation or a fresh schema instead.
- Before you read back saved data through JPA, call `flush()` and `clear()`, or read with plain JDBC in a new transaction. Otherwise the first-level cache returns the object that the code saved, not the row in the database.
- Run the Flyway or Liquibase migrations on the real database engine. Test a new migration with existing data, not only with an empty schema.
- Never depend on the order of rows unless the query has `ORDER BY`.
- Check numeric precision and rounding for money columns.
- Check time zones for timestamp columns.

## 3. Required cases (when they apply)

- Insert with all fields; read back and compare all fields.
- Unique constraint violation.
- Update that changes only the intended columns.
- Delete or soft delete, and the effect on related rows.
- Rollback when a later step fails.
- Two concurrent updates of the same row: no lost update (version check or lock).

## 4. Seeded faults for this layer (for the fault seeder)

- Save call removed (the API still returns success)
- Wrong column mapping (two fields swapped)
- Missing transaction boundary (partial write on failure)
- Wrong status value saved
- Lost precision (rounding or truncation)
- Missing unique check in the code (relies on a constraint that does not exist)
