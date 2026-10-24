---
name: qa-navigator
description: "Route a QA request to the right qe-skills skill and give the next steps, when the request does not clearly match one skill. Use when: 'which QA skill should I use', 'where do I start with testing', 'help me test this', 'what QA should we do'. Not for: a request that clearly matches another skill (use that skill directly). Related: qa-project-context, test-strategy, risk-based-testing."
---

# qa-navigator

## Objective

Choose the smallest set of skills that answers the request, in the right order. Then start the first one. This skill is the last resort: when a request clearly matches a skill, use that skill directly.

## Context

Read `.agents/qa-project-context.md` if it exists. If it does not exist and the work needs project facts, start with `qa-project-context`.

## Workflow

1. Restate the goal of the user in one sentence. Name the target (feature, change, module, whole product) and the phase (requirements, design, build, review, run, release, after release).
2. Choose the skills from the map below. Choose at most three, and give the order.
3. Tell the user the plan in two or three lines. Then start the first skill.

## Skill map

| The user wants to | Skill |
|---|---|
| Record the project facts once | `qa-project-context` |
| Decide the QA direction for a product or a team | `test-strategy` |
| Plan the testing of a sprint or a release | `test-planning` |
| Decide where to test first and how deep | `risk-based-testing` |
| Find gaps in requirements or stories | `requirement-gaps` |
| Find edge, boundary and negative cases | `edge-case-hunter` |
| Design test cases with formal techniques | `test-case-designer` |
| Explore the product in time-boxed sessions | `exploratory-testing` |
| Write or fix unit tests | `unit-testing` |
| Test HTTP or GraphQL APIs | `api-testing` |
| Test persistence, migrations, data integrity | `database-testing` |
| Test events, queues and streams | `messaging-testing` |
| Check the agreement between consumer and provider | `contract-testing` |
| Automate browser or UI flows | `ui-automation` |
| Simulate external services | `service-virtualization` |
| Create and manage test data | `test-data-management` |
| Set up reliable test environments | `test-environments` |
| Run tests in the pipeline | `ci-cd-integration` |
| Test speed, load and capacity | `performance-testing` |
| Test security weaknesses | `security-testing` |
| Test accessibility | `accessibility-testing` |
| Test locales, translations and international formats | `localization-testing` |
| Test failure handling: timeouts, retries, outages | `resilience-testing` |
| Check a feature or design for testability | `testability-review` |
| Check quality after release: synthetic checks, canary, alerts | `production-testing` |
| Review the quality of tests | `testcase-reviewer` |
| Review tests or a change with a panel of personas | `test-review-panel` |
| Find what is not tested | `test-coverage-map` |
| Check if the tests catch injected faults | `mutation-probe` |
| Find the cause of a flaky test | `flaky-test-detective` |
| Find bugs in code | `bug-hunter` |
| Get a direct code review | `roast-my-code` |
| Compare the spec, the code and the tests | `spec-drift` |
| Run the tests and triage failures | `test-runner` |
| Find what a change can break | `change-impact` |
| Write a reproducible bug report | `bug-report` |
| Decide go or no-go for a release | `release-readiness` |
| Learn from an escaped defect | `quality-postmortem` |

## Common sequences

- New feature: `requirement-gaps` → `edge-case-hunter` → `test-case-designer` → the automation skill for the layer → `testcase-reviewer` → `mutation-probe`.
- Pull request: `change-impact` → `test-runner` → `testcase-reviewer` for the changed tests.
- AI-written change: `test-runner` → `test-review-panel`.
- New QA engineer on an old codebase: `qa-project-context` → `test-coverage-map` → `risk-based-testing` → `test-strategy`.
- Before a release: `risk-based-testing` → `release-readiness` → `production-testing` for the checks after the release.
- New design with no code yet: `testability-review` → `requirement-gaps` → `test-case-designer`.
- Multi-region release: `localization-testing` → `ui-automation` → `accessibility-testing`.
- Service with many dependencies: `resilience-testing` → `service-virtualization` → `performance-testing`.
- After an incident: `bug-report` → `quality-postmortem`.

## Done when

- The user knows the chosen skills, the order and the reason.
- The first skill has started.

## Related skills

- `qa-project-context`: the facts that all skills use.
- `test-strategy`: the long-term QA direction.
- `risk-based-testing`: where to focus.
