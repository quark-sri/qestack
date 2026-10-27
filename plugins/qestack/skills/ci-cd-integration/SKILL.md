---
name: ci-cd-integration
description: "Designs or fixes how tests run in the delivery pipeline: stages, quality gates, sharding, caching, reports, flaky test handling and post-deploy smoke checks. Use when the user says 'run tests in CI', 'pipeline is too slow' or 'add a quality gate'. Not for one flaky test (use flaky-test-detective)."
license: MIT
argument-hint: "[pipeline file, stage or test suite]"
---

# ci-cd-integration

## Objective

The pipeline decides what reaches users. If it is slow, people skip it; if it is flaky, people ignore it; if it does not block, it protects nothing. This skill designs a pipeline where fast checks run first, important checks block, failures come with evidence, and the run time stays within budget.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its pipeline, test commands, environments and quality goals.
2. If it does not exist, read the pipeline files and the build files. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which pipeline platform, and which pipeline files?
2. What is the time budget for a pull request check and for a deploy?
3. Which checks must block a merge, and which a deploy?
4. Which suites are slow or flaky today?

## Principles

1. **Fast first, fail early.** Static checks and unit tests, then API and integration tests, then end-to-end and non-functional tests.
2. **A gate blocks or it is not a gate.** A check that never fails the pipeline is a report.
3. **Evidence for every failure:** machine-readable test results, logs, traces, screenshots, coverage and mutation reports as artifacts.
4. **Parallel within budget:** shard long suites by time, and cache dependencies and build outputs.
5. **Flaky tests are defects.** Quarantine with an owner and a date, not silent retries.
6. **Test after deploy:** smoke checks in each environment after the deploy, with a rollback rule.

## Workflow

1. Draw the current pipeline: stages, checks, run times, failure rates.
2. Set the target stages and the gates. See [the pipeline recipes](references/pipeline-recipes.md) for the test report formats and the sharding commands of each stack.
3. Move checks to the right stage. Split slow suites into shards. Add caching.
4. Publish test results in a machine-readable format, and attach the evidence files to failed runs.
5. Define the flaky test policy: detect (repeated runs or history), quarantine with an owner, fix within a time limit.
6. Add the nightly or scheduled suites (full regression, performance, security scans), and smoke checks after each deploy.
7. Measure the result: run time, failure rate, time to fix a red build.

## Anti-patterns

- **Everything in one long stage.** Feedback comes late, and one failure hides others.
- **Automatic retries everywhere.** Real failures and flaky tests both turn green.
- **`|| true` after a test command.** The gate never blocks.
- **No artifacts.** A failure in the pipeline cannot be investigated.

## Done when

- The stages run from fast to slow, and the pull request check is within its time budget.
- The blocking gates are defined and really fail the pipeline.
- Test results and evidence are published for each run.
- A flaky test policy and post-deploy smoke checks exist.

## Related skills

- `test-environments`: the services that the pipeline starts.
- `test-runner`: the commands and the triage of failures.
- `contract-testing`: deploy compatibility checks.
- `release-readiness`: the release gate.
