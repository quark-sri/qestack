---
name: resilience-testing
description: "Tests behavior when a dependency fails: timeouts, retries, circuit breakers, fallbacks, partial failures, outages, recovery and graceful shutdown, with safe fault injection. Use when the user says 'chaos test' or asks 'what happens if the database is down'. Not for load (use performance-testing)."
license: MIT
argument-hint: "[service, dependency or failure scenario]"
---

# resilience-testing

## Objective

Dependencies fail, slow down and return strange answers. A resilient system keeps its important functions, limits the damage and recovers by itself. This skill tests that behavior on purpose, starting with small failures in a safe environment.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its architecture, dependencies, environments, service levels and risks.
2. If it does not exist, find the dependencies in the configuration and the code. Suggest `qa-project-context` once.

## Discovery questions

1. Which dependencies does the service call (databases, services, queues, caches, files), and which of them are critical?
2. What must still work when each dependency fails? What may degrade, and how?
3. Which timeouts, retries, breakers and fallbacks exist, and where are their settings?
4. In which environment can failures be injected safely?

## Principles

1. **Hypothesis first.** Write what must happen before the experiment: "when the payment service is down for 30 seconds, orders are accepted and paid later."
2. **Slow is worse than down.** A slow dependency exhausts threads and queues. Test latency, not only errors.
3. **Retries need a limit and idempotency.** Without them, retries multiply the load and duplicate the effects.
4. **Small blast radius.** Start in a test environment with one failure. Go to a production experiment only with an exit rule and an owner.
5. **Prove the recovery,** not only the failure: the system returns to normal without a manual repair, and no data is lost or duplicated.

## Workflow

1. Draw the dependencies and the critical functions. List the failure modes with [the failure catalog](references/failure-catalog.md).
2. For each important pair of function and dependency, write the hypothesis: the failure, the expected behavior, the signal that shows it and the recovery time.
3. Check the settings first: every outbound call has a timeout, retries have a limit and a backoff, and the breaker and the fallback exist.
4. Test the logic at a low level with a fake dependency that fails or is slow (see the stack recipe). Test the real behavior with failure injected between real components.
5. Run the experiment, watch the signals, and compare with the hypothesis. Stop at the exit rule.
6. Check the recovery: the failure ends, and the system returns to normal. Check for lost, stuck or duplicated work.
7. Report each hypothesis as confirmed or not, with the evidence, the user impact and a fix.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **Only "dependency is down" tests.** The slow and partial failures cause the large outages.
- **Infinite or immediate retries.**
- **A fallback that was never executed.** It often fails on first use.
- **A fixed sleep to wait for recovery.** Wait for a signal.
- **A production experiment with no exit rule or no owner.**

## Done when

- Each critical dependency has at least a slow and a down experiment, with a written hypothesis.
- Timeouts, retry limits, breakers and fallbacks are checked, and the results are confirmed or listed as defects.
- The recovery is proven, with no lost or duplicated work.
- Each finding has the impact and a fix.

## Related skills

- `service-virtualization`: the fake dependencies that fail on demand.
- `performance-testing`: the load that makes a slow dependency dangerous.
- `messaging-testing`: retries, ordering and dead letters in event flows.
- `production-testing`: the controlled experiment in production.
