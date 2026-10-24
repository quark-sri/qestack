# Test Plan: [FEATURE NAME]

**Feature**: `[###-feature-name]` | **Feature tag**: `feature-[###]` | **Date**: [DATE]
**Inputs**: `spec.md`, `plan.md`, `contracts/`, `data-model.md`, rulesets: [list]
**Status**: Draft | Reviewed (verdict: ...) | Approved

> Rules: Write this plan from the specification only. Do not read the implementation.
> Every expected result needs a source (spec example, contract, rule). If the spec is
> unclear, add an open question. Do not guess.

## 1. Requirement inventory

Copy every requirement ID from `spec.md`. Give acceptance scenarios their derived IDs
(`US<story>-AS<n>`). Give each edge case an `EC-##` ID.

| ID | Source | Summary | Risk (H/M/L) | Notes |
|---|---|---|---|---|
| FR-001 | spec.md | ... | H | |
| US1-AS1 | spec.md, User Story 1, scenario 1 | ... | M | |
| EC-01 | spec.md, Edge Cases | ... | M | |

## 2. Traceability table (machine-read by `qestack trace`)

Keep the column names. The first column holds ONE requirement ID. "Categories required"
lists the categories that the tests for this ID must cover. Use `n/a - <reason>` only for
an ID that tests in this repository cannot cover (a human must agree).

| Req ID | Requirement summary | Test cases | Categories required | Layer |
|---|---|---|---|---|
| FR-001 | ... | TC-001, TC-002, TC-003 | positive, boundary, negative | domain, api |
| US1-AS1 | ... | TC-001 | positive | api |
| EC-01 | ... | TC-004 | error | api, db |
| SC-001 | ... | - | n/a - measured by the performance suite | - |

## 3. Test cases

Repeat this block for each test case.

### TC-001: [short name]

- **Requirement IDs**: FR-001, US1-AS1
- **Category**: positive | negative | boundary | error | security | contract | idempotency | ...
- **Layer**: domain | api | db | kafka | ui (domain = unit tests of business rules; db and kafka = integration tests with containers). The fault seeder uses the same names.
- **Preconditions / test data**: [the test creates its own data: ...]
- **Action**: [request / method call / event]
- **Expected result (oracle)**:
  - Response: [status, exact field values]
  - State: [rows, columns, values]
  - Events: [topic, key, value fields, headers] or "no event"
  - Errors: [error code, message key]
- **Oracle source**: [spec.md FR-001 example "100.00 → 90.00" / contracts/orders.yaml#/...]
- **Must fail when**: [the defect this test must catch, for example "discount applied at 99.99"]

## 4. Coverage of ruleset checklists

For each layer that this feature touches, confirm the ruleset checklist:

- [ ] API: status, body values, headers, error payload, state, side effects, negative cases
- [ ] Database: row values, no duplicates, constraints, rollback
- [ ] Kafka: topic, key, value, headers, no event on failure, idempotent consumer, DLQ
- [ ] UI: business outcome, web-first assertions, no fixed waits

## 5. Open questions

| # | Requirement | Question | Impact on tests |
|---|---|---|---|
| Q1 | FR-003 | The event key is not defined. | TC-010 is blocked until it is clear. |

## 6. Out of scope

| Item | Reason | Who covers it |
|---|---|---|
