---
name: production-testing
description: "Verifies quality in production after release: synthetic checks, health checks, canary rollouts with exit rules, feature flags, alerts as tests and rollback drills. Use when the user says 'test in production', 'canary release', 'shift right' or 'post-deploy checks'. Not for the release decision (use release-readiness)."
license: MIT
argument-hint: "[service, release or critical journey]"
---

# production-testing

## Objective

Some defects appear only with real data, real traffic and real dependencies. This skill adds checks that run after the release, safely: they find a problem fast and limit the damage.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its critical journeys, environments, quality goals and monitoring.
2. If it does not exist, find the deployment and monitoring files. Suggest `qa-project-context` once.

## Discovery questions

1. Which journeys and numbers decide that the product works (orders placed, logins, payments, error rate, latency)?
2. How does a release reach users: all at once, in stages, behind flags?
3. What monitoring, alerts and on-call process exist, and who acts on an alert?
4. Which data can a check create in production, and how is it removed?

## Principles

1. **Safe by design.** A production check must not harm real users or real data. Use test accounts and tagged data, and keep every action reversible.
2. **Few checks, critical journeys.** A small set of reliable checks beats many that people ignore.
3. **An alert is a test.** It needs a clear condition, an owner, a way to act and a proof that it fires.
4. **Staged exposure with exit rules.** Roll out in steps. Write the numbers that stop or reverse each step before the rollout starts.
5. **Detection time matters.** Measure how long a defect lives in production, and reduce it.

## Workflow

1. List the critical journeys and the signals that show they work.
2. Define the checks with [the production checklist](references/production-checklist.md): the post-deploy smoke check, the synthetic journeys, the health checks and the signal checks (error rate, latency, business numbers).
3. For a staged rollout, define the steps, the observation time and the exit rule for each step (the numbers that stop or reverse the rollout).
4. Check each alert: the condition, the threshold, the owner and the action. Prove that it fires, with a controlled test of the signal in a safe environment or with the alert's own test function.
5. Define the data rules: test accounts, tagged data, cleanup, and the actions that are never allowed.
6. Plan the drills: rollback, flag off, restore. Run each one before it is needed.
7. Report the checks, the exit rules, the alerts that were proven, and the gaps with an owner.

## Anti-patterns

- **A green dashboard as proof.** A dashboard can hide the failing journey.
- **Alerts nobody owns,** or alerts that fire all the time until people ignore them.
- **Testing in production with real customer data or real payments.**
- **A rollout with no exit rule,** so a person decides under stress.
- **A rollback that was never tried.**

## Done when

- The critical journeys have a safe production check, with an owner.
- Each rollout step has an observation time and an exit rule.
- Each important alert has a condition, an owner and an action, and has been proven to fire.
- The rollback or flag-off path was tried at least once, or the gap is listed with an owner.

## Related skills

- `release-readiness`: the go or no-go decision before the release.
- `ci-cd-integration`: the post-deploy stage in the pipeline.
- `performance-testing`: load and capacity tests before the release.
- `quality-postmortem`: learns from the defects that production found.
