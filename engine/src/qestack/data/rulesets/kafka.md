# Ruleset: Kafka testing

All agents read this file when `kafka` is in `[project] rulesets` of `.qestack/project.toml`.

## 1. Producer tests: what to check

| Effect | Check |
|---|---|
| Event published | Exactly one event for one business action |
| Topic | The topic from the contract |
| Key | The exact key (it controls partition and ordering) |
| Value | Each important field with exact expected values; schema version |
| Headers | Correlation ID, event type, source, trace headers in the contract |
| Timing | The event is published only after the database commit (outbox or transaction) |
| No event on failure | A rejected request publishes nothing |
| No duplicates | Retries do not publish twice (when the contract requires it) |

## 2. Consumer tests: what to check

| Effect | Check |
|---|---|
| Processing | The state change that the event causes (database, API, next event) |
| Idempotency | The same event twice gives the same final state |
| Ordering | Events for the same key in order give the right final state |
| Poison message | A bad message goes to the dead-letter topic and does not block the partition |
| Retry | Temporary failures retry; permanent failures do not retry forever |
| Schema evolution | An event with an unknown optional field is accepted (when the contract says so) |

## 3. Rules

- Use polling with a timeout (Awaitility `await().atMost(...).untilAsserted(...)` in Java, a polling helper in .NET). Never use a fixed sleep.
- To prove that NO event was published, poll for a fixed, documented window, and say why the window is long enough. Use one shared helper for this.
- Use a unique consumer group for each test. Use a unique key or correlation ID in each test. Filter the records by that value. Then tests do not see each other's events.
- Use a real broker for integration tests (Testcontainers Kafka or Redpanda). An embedded broker is acceptable if the team accepts the differences.
- Deserialize the event with the contract schema, not with the production DTO class. If the test uses the production class, a schema error stays hidden.
- Check the key and the headers, not only the value.

## 4. Required cases (when they apply)

- Event content for each event type in the contract.
- No event when the business action fails.
- Duplicate delivery to the consumer (idempotency).
- Bad message to the consumer (dead-letter topic).
- Event order for the same key.

## 5. Seeded faults for this layer (for the fault seeder)

- Event not published on one code path
- Wrong key (for example customer ID instead of order ID)
- Missing or wrong header
- Field missing from the event value
- Event published before the database commit, or published when the transaction rolls back
- Event published twice on retry
- Consumer not idempotent (processes a duplicate twice)
- Consumer swallows a poison message without a dead-letter record
