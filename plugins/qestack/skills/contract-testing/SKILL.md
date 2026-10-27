---
name: contract-testing
description: "Sets up consumer-driven contract tests for APIs and events: provider verification, provider states, a broker, can-I-deploy checks and schema compatibility. Use when the user says 'contract test' or asks 'will this API change break clients'. Not for deep tests of one API (use api-testing)."
license: MIT
argument-hint: "[consumer, provider or interface]"
---

# contract-testing

## Objective

End-to-end tests between services are slow and fragile, and they find breaking changes late. A contract test checks the agreement between two parties in isolation: the consumer states what it needs, and the provider proves that it delivers it. The pipeline can then block a deploy that would break a consumer.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its services, API styles, messaging and pipeline.
2. If it does not exist, find the consumers and providers from the code, the configuration and the documentation. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which services talk to which, over which interfaces (HTTP, events, RPC)? Which teams own them?
2. Is there a contract tool or broker in use? Is there a schema registry for events?
3. Who changes an interface first, and how do teams agree on changes today?

## Principles

1. **The consumer defines what it uses,** not the whole provider interface. Fields that no consumer uses can change freely.
2. **Match on type and shape, not on exact data,** except where the consumer depends on a value.
3. **Provider states** set up the data that each interaction needs. They are part of the contract.
4. **Contracts are versioned and verified in the pipeline** of both sides. A deploy checks that the deployed versions are compatible.
5. **Events need compatibility rules too:** a schema registry check (for example backward compatible) or event contracts.

## Workflow

1. Map the interactions in scope: consumer, provider, interface, owner.
2. **Consumer side:** write a contract test for each interaction that the consumer uses. It describes the request (or the expected event) and the minimum response that the consumer needs, with type matchers. The test runs the consumer code against a mock provider that the tool creates from the contract.
3. **Publish** the contract to the broker or the shared repository, with the consumer version and branch.
4. **Provider side:** verify all relevant consumer contracts against the real provider (in process or a test instance), with provider states for the data.
5. **Pipeline:** run the consumer tests and the provider verification on each change. Before a deploy, check that this version is compatible with the deployed versions of the other side.
6. **Events:** register schemas, set the compatibility mode, and check compatibility in the pipeline before publishing a new version.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **The provider writes the consumer's contract.** It then tests what the provider thinks, not what the consumer needs.
- **Exact data matching everywhere.** The contract breaks on harmless data changes.
- **Contracts that never block a deploy.** Without the pipeline check, they are documentation.
- **Contract tests as functional tests.** Business rules belong in the provider's own tests.

## Done when

- Each consumer-provider interaction in scope has a consumer contract with type matchers.
- The provider verifies the contracts with provider states in its pipeline.
- A deploy step checks compatibility with the deployed versions.
- Event schemas have a compatibility rule that the pipeline checks.

## Related skills

- `api-testing`: the provider's behavior in depth.
- `messaging-testing`: event producers and consumers.
- `ci-cd-integration`: the verification and deploy checks.
- `spec-drift`: drift between the contract, the docs and the code.
