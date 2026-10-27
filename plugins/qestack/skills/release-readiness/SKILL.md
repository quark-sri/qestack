---
name: release-readiness
description: "Decides go or no-go for a release with evidence: exit criteria, test results by risk, open defects, non-functional results, rollback and monitoring readiness. Use when the user says 'go no-go' or asks 'are we ready to release'. Not for planning the testing (use test-planning)."
license: MIT
argument-hint: "[release, version or date]"
---

# release-readiness

## Objective

A release decision needs facts, not a feeling. This skill collects the evidence for one release and compares it with the exit criteria. Then it gives a clear recommendation, with the reasons and the owners: go, go with known risks, or no-go.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its release criteria, critical journeys, environments and pipeline.
2. If it does not exist, ask the user for the release criteria. Suggest `qa-project-context` once.
3. Read the test plan of the release, if one exists.

## Discovery questions

1. Which version, which changes, and which date?
2. What are the exit criteria? Who makes the final decision?
3. Where are the test results, the defect list and the monitoring dashboards?

## Workflow

1. **Scope:** the changes in the release, and their risk (see `risk-based-testing`).
2. **Evidence,** for the release candidate build and commit only:
   - test results by level, with skipped and quarantined tests listed
   - the coverage of the high-risk items (tested, partly tested, not tested)
   - open defects by severity, with the decision for each critical and major one
   - non-functional results (performance, security, accessibility) where the plan requires them
   - contract and compatibility checks for changed interfaces
   - data migrations tested on realistic data
3. **Operational readiness:** a rollback or a feature flag for each risky change, monitoring and alerts for the critical journeys, smoke checks after the deploy, on-call owners.
4. **Compare** each exit criterion with the evidence: met, not met, or not measured.
5. **Recommend:** GO, GO WITH RISKS (each risk with an owner and a mitigation), or NO-GO (the blocking items).

## Output

```
## Release readiness: <version>

Recommendation: GO | GO WITH RISKS | NO-GO

| Exit criterion | Evidence | Status |
|---|---|---|

Open risks: <risk> - owner - mitigation
Blocking items: ...
After release: smoke checks, monitors to watch, rollback trigger
```

## Anti-patterns

- **Evidence from an older build.** It proves nothing about the candidate.
- **Skipped or quarantined tests counted as passed.**
- **"No known bugs"** when the high-risk items were not tested.
- **No rollback plan** for a risky change.

## Done when

- Each exit criterion has evidence from the candidate build, or is marked "not measured".
- Each open critical or major defect has a decision.
- The recommendation states the risks with owners, or the blocking items.
- The post-release checks and the rollback trigger are defined.

## Related skills

- `test-planning`: the exit criteria.
- `risk-based-testing`: the high-risk items.
- `test-runner`: the current results.
- `quality-postmortem`: learn from what escaped.
- `test-review-panel`: a merged review of the release changes.
