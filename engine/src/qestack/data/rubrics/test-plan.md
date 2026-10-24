# Test Plan Rubric (plan review)

Version 1.0. The `qe-test-judge` agent uses this rubric in plan-review mode, before any test code exists.

## Inputs

`spec.md`, `plan.md`, `contracts/`, `data-model.md`, `test-plan.md`, the guidance files and `trace-plan.json` (from `qestack trace --plan-only`).

## Dimensions (score 0–4, each with evidence: a line in test-plan.md or spec.md)

### P1. Completeness

- **4:** Every required ID (FR, acceptance scenario, edge case) is in the traceability table. Each edge case in the spec has an `EC-##` ID.
- **2:** One or more IDs are missing, or edge cases have no IDs.
- **0:** Many IDs are missing.

### P2. Case depth

- **4:** Each requirement has the positive, negative, boundary and error cases that it needs. The plan uses the right design technique: equivalence classes, boundary values with the step of the data type, a decision table for a rule with two or more conditions, state transitions (also invalid ones) for status fields. Each exclusion has a reason.
- **2:** Some rules have only positive cases.
- **0:** Happy path only.

### P3. Oracle quality

- **4:** Each test case has a concrete expected result with a source (spec example, contract, rule). No case says only "works correctly" or "returns success".
- **2:** Some expected results are vague.
- **0:** Most expected results are vague or missing.

### P4. Observable effects

- **4:** Each case lists the effects to check (response, state, events, errors), as the rulesets require.
- **2:** Some cases check only the status or "no error".
- **0:** Effects are not listed.

### P5. Layer choice

- **4:** Each case is on the cheapest layer that can prove it (unit, API, integration, UI). UI is used only where needed.
- **2:** Many cases on a slow layer without a reason, or a rule that needs integration is only unit-tested.
- **0:** Layer choice is missing.

### P6. Ambiguity handling

- **4:** Spec ambiguities are listed as open questions. No case guesses a rule. `[NEEDS CLARIFICATION]` items are not tested as if they were clear.
- **2:** Some guesses are hidden in the cases.
- **0:** The plan invents rules.

### P7. Risk focus

- **4:** High-risk rules (money, security, data integrity, irreversible actions) have extra cases and are marked as high risk.
- **2:** Risk is not considered.

## Verdict

- Any dimension = 0 → **reject**
- P1 < 4 or P3 < 3 → **revise**
- Average < 3 → **revise**
- Otherwise → **accept**

## Output

Write `<runs_dir>/plan-review.json` (from `qestack context`):

```json
{
  "feature": "003-order-discount",
  "mode": "plan-review",
  "scores": {"P1": {"score": 4, "evidence": "test-plan.md:20-48"}, "...": {}},
  "verdict": "revise",
  "findings": [
    {"dimension": "P2", "evidence": "test-plan.md:31", "issue": "FR-002 has no boundary case at total = 0.00", "fix": "Add TC for total 0.00 (accepted) and -0.01 (rejected, ORD-400)"}
  ],
  "open_questions": ["FR-003: the event key is not defined in the spec"]
}
```
