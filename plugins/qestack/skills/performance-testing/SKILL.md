---
name: performance-testing
description: "Plan, write, run and analyze performance tests: goals from service levels, workload models from real traffic, load, stress, spike, soak and capacity tests, realistic data, think time and ramp-up, latency percentiles, throughput and error rates, resource use, bottleneck analysis, and regression checks in the pipeline. Use when: 'performance test', 'load test', 'how many users can it handle', 'response time is slow', 'stress test', 'soak test', 'capacity planning'. Not for: functional API checks (use api-testing) or frontend page speed only. Related: api-testing, test-environments, test-data-management, ci-cd-integration."
argument-hint: "[service, endpoint, journey or goal]"
---

# performance-testing

## Objective

Performance problems appear under load, with real data, after hours of running. A performance test answers a concrete question ("Can checkout keep the 95th percentile under 400 ms at 200 orders per second?") with numbers that the team can trust. This skill plans and runs such tests, and finds the bottleneck when the answer is no.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its environments, critical journeys and quality goals.
2. If it does not exist, ask the user for the service levels and the environment. Suggest `qa-project-context` once.

## Discovery questions

1. What is the question: a service level check, the maximum capacity, a regression check, a soak for leaks?
2. What are the targets: latency percentiles, throughput, error rate, resource limits?
3. What does real traffic look like: the mix of requests, the peak rate, the growth?
4. Which environment can take the load, and how close is it to production? Who must know before the test runs?
5. Which external services are involved, and may they receive load?

## Principles

1. **A goal before a script.** Each test answers a question with a pass or fail target.
2. **A realistic workload model:** the request mix, the arrival rate, the think time, and the data size from production metrics.
3. **Percentiles, not averages.** Report the 50th, 95th and 99th percentiles, the throughput and the error rate together.
4. **Open models for services:** drive a target arrival rate, so that a slow system does not reduce the load on itself.
5. **Measure the system too:** CPU, memory, garbage collection, connection pools, queues, database waits. A number without a cause does not help.
6. **Same conditions each run** for regression checks: the same environment, data, version and load.

## Workflow

1. State the question and the targets.
2. Build the workload model: the scenarios, their share, the rate over time (ramp-up, steady state, peak), and the data.
3. Choose the test type: load (expected peak), stress (beyond the peak until failure), spike (a sudden jump), soak (hours at a normal rate), capacity (step up until a target breaks).
4. Write the scripts with the project's load tool. Use unique data, real authentication, and checks on each response (a fast error is not a success).
5. Prepare the environment: data volume, monitoring, simulated third parties if they may not receive load. Tell the owners.
6. Run a short smoke run, then the real run. Record the version, the environment and the settings.
7. Analyze: percentiles over time, errors by type, saturation points in the resource metrics, the first component that reaches its limit.
8. Report the answer, the evidence and the bottleneck. For a regression check, compare with the baseline and fail on a stated threshold.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **Averages only.** They hide the slow requests that users feel.
- **A closed loop of a few virtual users** with no think time, that measures the tool and not the system.
- **Tiny test data.** Indexes, caches and queries behave differently at production volume.
- **No response checks.** Fast errors look like good performance.
- **Load on a shared environment or a third party** without telling anyone.

## Done when

- The question and the targets are stated, and the workload model is documented.
- The run used realistic data, checked the responses and recorded the conditions.
- The report gives percentiles, throughput, errors and resource use, and a pass or fail for each target.
- A bottleneck is named with evidence, or the absence of one is shown.

## Related skills

- `api-testing`: functional checks before load.
- `test-environments`: an environment that can take the load.
- `test-data-management`: data at production volume.
- `ci-cd-integration`: regression checks in the pipeline.
