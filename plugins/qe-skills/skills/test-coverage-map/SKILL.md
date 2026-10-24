---
name: test-coverage-map
description: Map what is tested and what is not, by requirement, feature, user journey, code area and test level, not only by line coverage. Shows untested requirements, untested risky code, areas tested only by weak or end-to-end tests, and the shape of the test pyramid. Use when the user asks "what is not tested?", "where are our coverage gaps?", or needs a coverage overview for a team, an audit or a release.
argument-hint: "[repository, module, feature or requirement set]"
---

# test-coverage-map

Line coverage shows which lines ran. It does not show which rules are checked. This skill maps the tests to requirements and to code areas, and shows the real gaps.

## Input

The scope is `$ARGUMENTS`. If it is empty, use the whole repository and say so. Find the requirement sources (specs, stories, contracts, documentation) and the tests.

## Steps

1. **Inventory the tests.** For each test file, note the level: unit, component or API, integration, contract, or end-to-end UI. Also note the area that it tests, and the requirement IDs or behaviors that it names.
2. **Inventory the targets:**
   - requirements and acceptance criteria (with IDs if they exist)
   - code areas: modules, services, public functions and endpoints
   - user journeys from the documentation or the UI
3. **Map** each test to the targets. Use explicit links first (IDs in names, tags, comments). Then use the code that the test calls. Mark each link as explicit or inferred.
4. **Rate each target:**
   - COVERED: at least one strong test (it checks values or effects, not only status or existence)
   - WEAK: only weak tests, or only end-to-end tests for a business rule
   - UNTESTED: no test
5. **Line coverage (optional).** If the project already has a coverage report, read it. If not, ask the user before you run the coverage command of the project. Mark risky code with no coverage: error paths, validation, calculations, permission checks.
6. **Test pyramid.** Count the tests at each level. Name problems such as many UI tests and few unit tests, or no integration tests for database or messaging code.
7. **Rank the gaps** by risk (impact × likelihood).

## Output

```
## Test coverage map: <scope>

| Level | Tests | Share |
|---|---|---|

### Requirements
| Req / behavior | Status | Tests (explicit / inferred) | Note |
|---|---|---|---|

### Code areas
| Area | Status | Line coverage | Risky untested paths |
|---|---|---|---|

### Top gaps to close
1. <target>: <why it matters>. Add: <test at which level>
```

## Rules

- Say which links are inferred. An inferred link can be wrong.
- A requirement covered only by weak tests is not covered. Say so.
- Do not run long or costly commands without asking the user.
