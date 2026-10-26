---
name: risk-based-testing
description: "Builds a risk matrix (impact times likelihood, with evidence) for a product, release or change, sets the test depth for each risk zone and analyzes the top failure modes. Use when the user says 'risk assessment' or asks 'where should we focus testing'. Not for the long-term QA direction (use test-strategy)."
argument-hint: "[product area, release, feature or change]"
---

# risk-based-testing

## Objective

Testing time is limited. Equal effort on every area wastes it on low-risk areas and leaves critical areas weak. This skill scores the risks with evidence, decides the test depth for each risk zone, and keeps the decision visible.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its risk areas and critical journeys.
2. If it does not exist, find the facts in the repository and the documentation. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which flows earn money or have a contract with penalties?
2. What broke in the last releases, and why?
3. Which areas change often, or are complex, or have weak tests?
4. Which external services, data migrations or configuration changes are involved?
5. Who confirms the impact scores (a product owner, a business owner)?

## Workflow

1. **Areas.** Split the scope into areas that the business understands: features, user journeys, services, integrations, data flows.
2. **Impact (1–5)** for each area: what happens if it fails in production?
   - 5: money is lost, security or privacy is broken, data is lost or wrong, a legal rule is broken, many users are blocked
   - 3: some users get a wrong result, and a workaround exists
   - 1: cosmetic, rare, easy to notice and fix
3. **Likelihood (1–5)** for each area, from evidence:
   - recent change volume (version control history)
   - complexity: long functions, many branches, much shared state, asynchronous steps
   - defect history (tracker, fix commits, incident notes)
   - weak or missing tests, flaky tests
   - unclear or late requirements, new technology, a new team
4. **Score** = impact × likelihood. Sort.
5. **Failure modes** for the top five risks: how can it fail, how would we notice, which test or monitor catches it.
6. **Test depth** for each zone:
   - 15–25: formal design techniques, negative and boundary cases, integration and contract tests, a test review, exploratory sessions, a monitor in production
   - 8–14: the main paths, key boundaries and errors
   - 1–7: smoke checks
7. **Coverage alignment.** Compare the depth with the current tests (see `test-coverage-map`). List the gaps.
8. **Reassessment triggers:** an incident, a large change, a new integration, a new regulation.

## Output

```
## Risk matrix: <scope>

| Area | Impact | Likelihood | Score | Evidence | Test depth | Current tests | Gap |
|---|---|---|---|---|---|---|---|

### Failure modes (top 5)
| Area | Failure mode | Detection | Test or monitor |

### Assumptions to confirm
- ...
```

## Anti-patterns

- **Risk theater.** Scores without evidence, made once and never updated.
- **Impact chosen by testers alone.** Impact is a business decision. Ask the owner to confirm it.
- **Only technical risk.** A simple feature that moves money is high risk.

## Done when

- Each area has an impact and a likelihood with a reason, or is marked as a guess.
- The top risks have failure modes and a planned detection.
- Each risk zone has a test depth, and the gaps against the current tests are listed.
- The impact scores are confirmed by the user or listed as open.

## Related skills

- `test-strategy`: uses the matrix for long-term decisions.
- `test-planning`: uses it for one sprint or release.
- `test-coverage-map`: shows the current tests for each area.
- `release-readiness`: checks the top risks before a release.
