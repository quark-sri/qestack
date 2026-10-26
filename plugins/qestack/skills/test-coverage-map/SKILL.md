---
name: test-coverage-map
description: "Maps what is tested and what is not by requirement, journey, code area and test level, not only line coverage, and shows the pyramid shape. Use when the user asks 'what is not tested' or 'which requirements have no tests'. Not for the quality of each test (use testcase-reviewer)."
argument-hint: "[repository, module, feature or requirement set]"
---

# test-coverage-map

## Objective

Line coverage shows which lines ran. It does not show which rules are checked, or which requirements have no test. This skill maps the tests to requirements and to code areas, rates each target as covered, weak or untested, and ranks the gaps by risk.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test levels, requirement sources and coverage reports.
2. If it does not exist, find the tests, the requirement sources and any coverage report in the repository. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. What is the scope: the whole repository, a module, a feature, a set of requirements?
2. Where are the requirements (specs, stories, contracts, documentation)?
3. Does a coverage report exist, or may the coverage command run?

## Workflow

1. **Inventory the tests.** For each test file, note the level: unit, component or API, integration, contract, or end-to-end UI. Note the area that it tests, and the requirement IDs or behaviors that it names.
2. **Inventory the targets:** requirements and acceptance criteria, code areas (modules, services, public functions, endpoints), and user journeys.
3. **Map** each test to the targets. Use explicit links first (IDs in names, tags, comments), then the code that the test calls. Mark each link as explicit or inferred.
4. **Rate each target:** COVERED (at least one strong test that checks values or effects), WEAK (only weak tests, or only end-to-end tests for a business rule), UNTESTED.
5. **Line coverage.** Read an existing report, or run the coverage command with the user's agreement. Mark risky code without coverage: error paths, validation, calculations, permission checks.
6. **Test pyramid.** Count the tests at each level, and name the shape problems.
7. **Rank the gaps** by risk (see `risk-based-testing`).

## Output

```
## Test coverage map: <scope>

| Level | Tests | Share |
|---|---|---|

| Requirement / behavior | Status | Tests (explicit / inferred) | Note |
|---|---|---|---|

| Code area | Status | Line coverage | Risky untested paths |
|---|---|---|---|

Top gaps to close: <target> - why - the test to add, and its level
```

## Anti-patterns

- **Line coverage as the answer.** A covered line with no assertion is not tested.
- **Inferred links shown as facts.** Mark them.
- **Equal weight for all gaps.** An untested permission check matters more than an untested log line.

## Done when

- Each requirement and code area in scope has a status, with explicit or inferred links.
- The test pyramid shape is described.
- The top gaps are ranked by risk, each with the test to add.

## Related skills

- `risk-based-testing`: the risk of each gap.
- `testcase-reviewer`: the quality of the tests that exist.
- `mutation-probe`: whether covered code is really checked.
- `test-strategy`: the target shape of the suite.
