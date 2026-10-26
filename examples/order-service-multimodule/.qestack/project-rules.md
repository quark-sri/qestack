# Project rules: <project name>

> Fill in this file for your project. All agents read it. Keep it short and specific.
> Agents must not edit it (protected). Change it with a human review.

## 1. System under test

- Service name and purpose:
- Main modules and where they are (paths):
- External dependencies (database type, Kafka topics, other services):

## 2. Test locations and naming

| Test type | Folder | Class suffix | Tags |
|---|---|---|---|
| Unit | `src/test/java/...` | `*Test` | category + IDs |
| API (component) | `src/test/java/.../api` | `*ApiTest` | category + IDs |
| Integration (DB, Kafka) | `src/it/java/...` | `*IT` | `integration` + IDs |
| UI (future) | `src/test/java/.../ui` | `*UiTest` | `ui` + IDs |

## 3. Internal HTTP client library

- Library name and package:
- How to create a client in a test:
  ```java
  // example: var api = TestApiClient.forService("orders").withAuth(TestUsers.CUSTOMER);
  ```
- Assertion methods (also list them in `.qestack/project.toml` → `extra_custom_assertion_regexes`):
  - `...assertStatus(...)` (status only: not enough alone)
  - `...assertBody(...)`
- Authentication helpers and test users:

## 4. Database

- Engine and version:
- How tests get a database (Testcontainers / shared schema / rollback):
- How to read state in a test (helper class, SQL, repository that is not under test):

## 5. Kafka

- Topics and their contracts (schema location):
- Test helper to consume and filter events:
- Default polling timeout:

## 6. Test data

- Builders / factories to use:
- Data that must never be used (production-like IDs, shared accounts):

## 7. Known exclusions

- Modules or packages excluded from mutation testing, with the reason:
- Requirements that are tested outside this repository (performance, security scans), with the reason:

## 8. Extra rules for this project

-
