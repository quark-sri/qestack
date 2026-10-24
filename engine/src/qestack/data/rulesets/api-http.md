# Ruleset: HTTP API testing

All agents read this file when `api-http` is in `[project] rulesets` of `.qestack/project.toml`. It applies to any HTTP client: an internal shared library, Java `HttpClient`, Apache HttpClient, RestAssured, `HttpClient` in .NET, or a framework test client.

## 1. What a complete API test checks

A status code alone proves very little. For each API test case, check all of the effects that the contract defines:

| Effect | Check | Example |
|---|---|---|
| Status | Exact code from the contract | `201`, not "2xx" |
| Body values | Each important field with the exact expected value from the spec | `total = 90.00`, `status = "DISCOUNTED"` |
| Body shape | Required fields exist; no unexpected fields if the contract forbids them | JSON schema or field-by-field |
| Headers | Headers in the contract | `Location`, `Content-Type`, `ETag`, correlation ID |
| Error payload | Error code, message key, field errors | `code = "ORD-400"`, `field = "total"` |
| Persisted state | Database row or a follow-up GET | Order saved with the right values |
| Side effects | Events, calls to other services | Kafka event published once |
| No side effect on failure | A rejected request changes nothing | No row, no event |

The judge scores R3 (assertion depth) against this table.

## 2. Required negative cases for each endpoint

The test designer adds these cases to `test-plan.md` when they apply. If one does not apply, the plan says why.

- Missing required field
- Wrong type or format (for example a string where a number is required)
- Value out of range (boundary - 1, boundary + 1)
- Unknown or extra field (if the contract rejects it)
- Not found (unknown ID)
- Conflict (duplicate create, version mismatch)
- Authentication missing or invalid → 401
- Authorization: valid user, wrong role or wrong tenant → 403
- Idempotency: same request twice (when the contract requires idempotency)
- Unsupported media type or method

## 3. Oracles

- Take expected values from `spec.md` examples, from `contracts/` (OpenAPI) and from `data-model.md`.
- Write the expected value as a literal in the test, or build it from test data that the test itself creates. Do not call production code to compute it.
- If the spec gives no example for a rule, the designer adds an open question. The writer does not guess.

## 4. Internal HTTP client library

Your project uses an internal shared library on top of `HttpClient`. Rules:

- Use the library for requests. Do not build raw connections in tests.
- Register the assertion methods of the library in `.qestack/project.toml` (`extra_custom_assertion_regexes`). Otherwise the lint gate reports false "no assertion" findings.
- If the library has a "check status" helper, also check the body. The helper alone makes the test SHALLOW.
- Do not catch and ignore exceptions from the library. Let them fail the test.
- Write project-specific details (base URL setup, authentication helper, test data builders) in `.qestack/project-rules.md`.

## 5. Test isolation

- Each test creates its own data (unique IDs, unique names). Never depend on data from another test.
- Clean up through the API or let the database container reset. Do not leave data that changes other tests.
- Do not use fixed sleeps to wait for the server. Use a readiness check or polling with a timeout.

## 6. Seeded faults for this layer (for the fault seeder)

- Wrong status code for an error case
- Missing validation of a required field
- Wrong field in the response (mapping error, rounding error)
- Missing authorization check for a role or tenant
- Missing header (`Location`)
- Error payload with a wrong error code
- Create returns success but does not save
