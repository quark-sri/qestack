---
name: messaging-testing
description: "Tests event-driven systems with a real broker: producers, consumers, keys, headers, schemas, idempotency, ordering, retries, dead letters and outbox flows, without fixed sleeps. Use when the user says 'Kafka test', 'queue test' or 'test this consumer'. Not for HTTP endpoints (use api-testing)."
argument-hint: "[producer, consumer, topic, queue or event flow]"
---

# messaging-testing

## Objective

Asynchronous systems fail in quiet ways. Examples: an event with the wrong key, an event for a rolled-back transaction, a duplicate processed twice, a poison message that blocks a partition. This skill tests producers, consumers and flows against a real broker, and waits for results without fixed sleeps.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its broker, schema format, environments and conventions.
2. If it does not exist, find them in the configuration, the event schemas and the existing tests. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. Which broker and which delivery guarantee (at least once, exactly once in a transaction)?
2. Where are the event contracts (schema files, a schema registry, documentation)?
3. How does the producer publish: directly, in a transaction, or through an outbox table?
4. What must a consumer do with a duplicate, an out-of-order event and a bad message?

## Principles

1. **A real broker for integration tests.** Embedded or fake brokers differ in transactions, ordering and retries.
2. **Wait for conditions, never for time.** Poll for the expected result with a timeout.
3. **Isolate each test** with a unique key or correlation ID, and filter the records by it. Use a unique consumer group for each test consumer.
4. **Decode with the contract schema,** not with the production class. Otherwise a schema error stays hidden.
5. **Prove "no event" without waiting when you can:** check an outbox table, or send a second "barrier" event on the same key that must arrive first. Use a polling window only as the last option, and state why it is long enough.

## Workflow

1. List the producers and consumers in scope, with their events and rules. Use [the messaging checklist](references/messaging-checklist.md).
2. Start the broker (and a schema registry if the project uses one) for the tests.
3. **Producer tests:** trigger the business action, then consume from the topic or queue. Check exactly one event, the key, each important value, the headers, and the schema. For a failed action, check that no event exists. For a transactional producer, read only committed records.
4. **Consumer tests:** publish an event, then wait for the state change. Then publish the same event again and check that the state is the same. Publish events out of order and a bad message, and check the dead-letter record and its headers.
5. **Flow tests** for the critical chains: the first action to the last effect, with a correlation ID.
6. Run the tests several times (see `flaky-test-detective`). Asynchronous tests must be stable.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own client, and say so.

## Anti-patterns

- **Fixed sleeps** before the assertion. Slow and flaky.
- **One shared consumer group** for all tests. Tests steal each other's events.
- **Reading from the end of the topic** after the action. The event can be missed.
- **Checking only the value.** The key controls partitioning and order; headers carry trace and type data.
- **Uncommitted reads** in producer tests. An event from a rolled-back transaction looks real.

## Done when

- Each producer has tests for one event per action, key, value, headers, schema, and no event on failure.
- Each consumer has tests for processing, duplicates, ordering where it matters, and the dead-letter path.
- The tests use a real broker, wait by condition, and pass in repeated runs.

## Related skills

- `database-testing`: the commit and outbox side of events.
- `contract-testing`: event schemas shared with other teams.
- `test-environments`: broker containers.
- `flaky-test-detective`: when an asynchronous test is unstable.
