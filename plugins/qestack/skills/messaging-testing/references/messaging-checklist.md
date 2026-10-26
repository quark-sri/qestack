# Messaging test checklist

## Producer

| Effect | Check |
|---|---|
| Count | Exactly one event for one business action |
| Destination | The topic, queue or routing key from the contract |
| Key | The exact key (it controls partition and order) |
| Value | Each important field with the exact expected value; the schema version |
| Headers | Correlation ID, event type, source, trace headers in the contract |
| Timing | Published only after the database commit (outbox or transaction) |
| Failure | A rejected or rolled-back action publishes nothing |
| Retries | A retry does not publish twice (when the contract requires it) |

## Consumer

| Effect | Check |
|---|---|
| Processing | The state change that the event causes (database, API, next event) |
| Idempotency | The same event twice gives the same final state |
| Ordering | Events for the same key in order give the right final state; out-of-order events are handled as the rule says |
| Poison message | A bad message goes to the dead-letter destination with the original topic, partition, offset and the error, and does not block the others |
| Retry | Temporary failures retry with a limit; permanent failures do not retry forever |
| Schema evolution | An event with an unknown optional field is accepted (when the contract says so) |

## Test consumer settings (stream brokers)

- Read only committed records (for example `isolation.level=read_committed`).
- Start from the earliest offset with a unique group, or wait for the partition assignment before the action.
- Filter by the test's unique key or correlation ID.
