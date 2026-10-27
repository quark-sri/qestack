---
name: test-environments
description: "Sets up reproducible test environments: containers, production engine versions, readiness checks, isolated parallel runs and preview environments. Use when the user says 'test environment' or 'tests fail in CI every time'. Not for intermittent failures (use flaky-test-detective) or test data (use test-data-management)."
license: Apache-2.0
argument-hint: "[service, test suite or environment]"
---

# test-environments

## Objective

A test is only as trustworthy as the environment it runs in. Shared, drifting environments make results depend on the day and on other teams. This skill sets up environments that start the same way each time, match production where it matters, and do not leak state between runs.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its environments, services and pipeline.
2. If it does not exist, find them in the container files, the configuration and the pipeline. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which services does each test level need (database, broker, cache, search, object storage, other services)?
2. Which versions run in production?
3. Where do tests run: developer machines, pipeline agents, shared test environments? Are containers available there?
4. What differs between the test environment and production today?

## Principles

1. **Disposable over shared.** Start dependencies for each run or each test class, in containers. Use shared environments only for what cannot run locally.
2. **Production parity where it matters:** the same engine and major version, the same configuration flags, the same time zone and locale rules.
3. **Configuration from the environment,** not from code. The same build runs everywhere.
4. **Ready means ready.** Wait for a health check or a log line, never for a fixed time.
5. **Isolation for parallel runs:** random ports, a schema or a namespace for each worker, unique resource names.

## Workflow

1. List the dependencies for each test level and their production versions.
2. Start each dependency for tests with a container library or a compose file. Pin the image versions.
3. Wire the configuration: pass the dynamic addresses and credentials to the application through environment variables or test properties.
4. Add readiness checks, and a clear error message when a dependency does not start.
5. Make parallel runs safe: random ports, separate schemas or namespaces, unique names.
6. Write a short parity table: each difference from production, its risk, and how other tests cover it.
7. For pull requests, consider an ephemeral environment with the changed services and simulated third parties.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **One shared database** for all developers and pipelines.
- **"latest" image tags.** Results change without a code change.
- **Fixed sleeps** while a service starts.
- **Hard-coded hosts and ports** in test code.
- **A staging that nobody owns,** with old data and hand-made changes.

## Done when

- Each test level starts its dependencies the same way locally and in the pipeline, with pinned versions.
- Configuration comes from the environment; readiness is checked.
- Parallel runs do not collide.
- The differences from production are listed with their risk.

## Related skills

- `test-data-management`: the data inside the environment.
- `service-virtualization`: third-party services in the environment.
- `ci-cd-integration`: the environment in the pipeline.
- `database-testing`: database containers.
