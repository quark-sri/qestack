# Test Quality Report: 001-order-discount

Generated: 2026-10-24T08:45:12Z | Iteration: 1 | Tool: qestack 0.1.0

## Decision: **CONTINUE**

improve the tests with the feedback file.

**Test Quality Score: 26.8** (minimum 80) (partial: some inputs are missing)

## 1. Hard gates

| Gate | Status | Value | Target | Note |
|---|---|---|---|---|
| hollow | FAIL | 1 | <= 0 |  |
| no_assertion | PASS | 0 | <= 0 |  |
| skipped | FAIL | 1 | <= 0 |  |
| trivial | FAIL | 1 | <= 0 |  |
| shallow | FAIL | 2 | <= 0 |  |
| trace | FAIL | 0% | >= 100% |  |
| red | FAIL | 50% | >= 100% | OK |
| flaky | PASS | 0 | <= 0 |  |
| failing | PASS | 0 | <= 0 | each failing test is a test defect or a product bug |
| mutation | FAIL | 47% | >= 75% |  |
| seed | FAIL | 0% | >= 90% |  |
| guard | NOT_RUN | n/a | 0 |  |
| judge | NOT_RUN | n/a | 0 |  |

## 2. Score dimensions

| Dimension | Score | Weight |
|---|---|---|
| fault detection | 28.0 | 35% |
| requirement depth | 0.0 | 25% |
| assertion strength | 20.0 | 15% |
| independence | n/a | 15% |
| maintainability | 100.0 | 10% |

## 3. Requirement traceability

Coverage 0% (0/6), depth 0%, orphan tests 0, unknown IDs 0, excluded by test plan 0.

| ID | Tests | Categories | Status |
|---|---|---|---|
| FR-001 | 0 | - | UNCOVERED |
| FR-002 | 0 | - | UNCOVERED |
| FR-003 | 0 | - | UNCOVERED |
| US1-AS1 | 0 | - | UNCOVERED |
| US1-AS2 | 0 | - | UNCOVERED |
| US1-AS3 | 0 | - | UNCOVERED |

## 4. Surviving mutants

Each line is a code change that no test detected.

- `src/main/java/com/example/order/Discount.java:13` ConditionalsBoundaryMutator: changed conditional boundary (survived)
- `src/main/java/com/example/order/Discount.java:13` RemoveConditionalMutator_ORDER_IF: removed conditional - replaced comparison check with true (survived)
- `src/main/java/com/example/order/Discount.java:13` BooleanTrueReturnValsMutator: replaced boolean return with true for com/example/order/Discount::appliesTo (survived)
- `src/main/java/com/example/order/Discount.java:17` RemoveConditionalMutator_EQUAL_ELSE: removed conditional - replaced equality check with false (survived)
- `src/main/java/com/example/order/Discount.java:17` RemoveConditionalMutator_EQUAL_IF: removed conditional - replaced equality check with true (survived)
- `src/main/java/com/example/order/OrderException.java:14` EmptyObjectReturnValsMutator: replaced return value with "" for com/example/order/OrderException::code (no_coverage)
- `src/main/java/com/example/order/OrderService.java:16` ConditionalsBoundaryMutator: changed conditional boundary (survived)
- `src/main/java/com/example/order/OrderService.java:20` RemoveConditionalMutator_EQUAL_IF: removed conditional - replaced equality check with true (survived)

## 5. Seeded faults not detected

- **F01** [FR-001 / domain] UNDETECTED
- **F04** [FR-001 / domain] UNDETECTED
- 2 held-out fault(s) not detected

Fault details for humans: `.qestack/runs/001-order-discount/faults/undetected.md` (not committed).

## 8. Items for human decision

- Test passed before implementation: `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.discountIsCalculated` (fix the test, or add it to the red exemption file if the behavior already existed)
- Test passed before implementation: `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.boundaryValues` (fix the test, or add it to the red exemption file if the behavior already existed)

## 9. Human audit sample

Read only these tests. Record your verdict (accept / revise / reject) in `.qestack/runs/001-order-discount/human-audit.json`. Then run `qestack calibrate`.

- [random] `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.eventIsPublished`
- [random] `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.boundaryValues`
- [random] `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.noEventBelowTheLimit`
- [random] `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.discountIsCalculated`
- [random] `src/test/java/com/example/order/WeakDiscountTest.java::WeakDiscountTest.negativeTotalIsRejected`

