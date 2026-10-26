---
name: test-strategy
description: "Write a test strategy for a product, a system or a team: quality goals, test levels and their share, what each level owns, environments, test data, automation and manual scope, non-functional testing, entry and exit criteria, metrics and a roadmap. Use when: 'test strategy', 'QA strategy', 'how should we test this system', 'QA roadmap', 'test pyramid for our services'. Not for: one sprint or release plan (use test-planning) or the risk scores (use risk-based-testing first). Related: risk-based-testing, test-planning, qa-project-context, test-coverage-map."
argument-hint: "[product, system or team]"
---

# test-strategy

## Objective

A test strategy says how a team gets confidence in quality, and at what cost. It decides which test level owns which risk, so that each defect class has a cheap place where it is caught. The output is a short document that a team can follow and review each quarter.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use it, and skip the questions that it answers.
2. If it does not exist, find the facts in the repository and the documentation. Suggest `qa-project-context` once. Do not stop the work for it.
3. If a risk matrix exists, use it. If not, do a short version of `risk-based-testing` first.

## Discovery questions

1. What is the business goal for quality: fewer incidents, faster releases, a compliance need, lower test cost?
2. Which failures hurt most: money, data, security, availability, user trust?
3. What is the release rhythm and how long may the pipeline take?
4. Which test levels exist today, and which of them catch real defects?
5. Who writes and owns the tests: developers, QA engineers, both?
6. Which external systems and teams are involved, and who owns their contracts?

## Principles

1. **Each risk has an owner level.** Business rules belong in fast unit and API tests. Wiring and infrastructure belong in integration tests. Agreements between teams belong in contract tests. Only a few critical journeys belong in end-to-end tests.
2. **Fast feedback first.** A defect found in seconds costs less than one found in a nightly run.
3. **Evidence over coverage numbers.** Measure if tests catch defects (escaped defects, mutation score, fault injection), not only which lines ran.
4. **Automate the repeatable, explore the unknown.** Automated checks protect known behavior. Exploratory sessions find new risks.
5. **Non-functional needs are planned, not added late.** Performance, security, accessibility and resilience have owners and criteria.

## Workflow

1. **Current state.** Describe the test levels, their size, their run time, their flakiness and the escaped defects of the last releases.
2. **Risks.** List the top risks with their impact and likelihood.
3. **Level ownership.** For each risk class, choose the level that catches it at the lowest cost. Write the target shape (the share of tests for each level), with a reason.
4. **Scope.** In scope and out of scope, for each system and each quality attribute.
5. **Environments and data.** Which environment runs which level. Which services are real or simulated. How test data is created and cleaned.
6. **Automation approach.** Frameworks by level (use the project's own), naming and tagging, where tests live, how they run in the pipeline, who maintains them.
7. **Non-functional testing.** Criteria and timing for performance, security, accessibility and resilience.
8. **Entry and exit criteria** for a change, a release and a hotfix.
9. **Metrics.** A few that change decisions: escaped defects by level, flaky test rate, pipeline time, mutation score of critical modules, time to fix a broken build.
10. **Roadmap.** The next three steps, with an owner and a date.

## Anti-patterns

- **An inverted pyramid.** Most checks in slow end-to-end tests. The suite becomes slow and flaky, and business rules are tested through the UI.
- **Strategy as a template.** A document with generic text that nobody follows. Each statement must change a decision.
- **Coverage as the goal.** A coverage target alone rewards tests that run code but check nothing.
- **No owner.** A strategy without owners and dates does not change anything.

## Done when

- Each top risk has an owner level and a test approach.
- The target test shape, environments, data approach and pipeline stages are stated with reasons.
- Entry and exit criteria and three to five metrics are defined.
- The roadmap has owners and dates, and the user has reviewed the open points.

## Related skills

- `risk-based-testing`: the risk scores that drive the strategy.
- `test-planning`: applies the strategy to one sprint or release.
- `test-coverage-map`: shows the current state.
- `ci-cd-integration`: puts the levels into the pipeline.
