# Failure catalog

| Failure | How to inject it | What to check |
|---|---|---|
| Connection refused | Stop the dependency, or point to a closed port | Fast error, a clear message, the fallback, no thread stuck |
| Timeout | Accept the connection and never answer | The call stops at the timeout. The caller does not wait without a limit |
| Slow answers | Add a fixed delay to each answer | Timeouts hold, the pools do not run out, other functions still work |
| Slow then fast | A delay that ends after some time | The system recovers without a restart |
| Error responses | Return 500, 503 or 429 for some or all calls | Retries stop at the limit and use backoff. The breaker opens |
| Malformed response | Wrong schema, empty body, a truncated body | A handled error, not a crash. No bad data is stored |
| Partial failure | Fail one call out of a batch, or fail after a write | No half-done state. Retries do not duplicate the effect |
| Dropped connection | Cut the connection in the middle of a call | The client retries only when it is safe (idempotent) |
| Dependency outage for minutes | Stop it for a longer time | Queues and buffers have limits. Work resumes in order after the recovery |
| Database failure | Stop it, fail over, fill the connection pool | A clear error. Transactions roll back. The pool recovers |
| Queue or broker failure | Stop the broker, fail a consumer | No message lost. No duplicate effect. Dead-letter handling works |
| Cache failure | Stop the cache, or return stale data | The system works without the cache, and the database can take the load |
| Clock jump and slow time | Move the clock | Expiry, tokens and schedules are right |
| Restart and shutdown | Kill the process, send a stop signal during work | Work in progress finishes or restarts safely. No data is lost |
| Resource limits | Low memory, full disk, no file handles | A clear error and an alert, not silent damage |

## The hypothesis sheet

| Failure | Function | Expected behavior | Signal | Recovery time | Result |
|---|---|---|---|---|---|
| Payment service slow (5 s) | Place order | Order accepted, payment marked pending, the user sees a message | Pending-payments count, p95 of the order call | Under 2 minutes after the fix | |

## Safety rules for a production experiment

- Written hypothesis, exit rule and an owner who watches.
- A small share of traffic, outside the busiest hours.
- An easy and tested way to stop the experiment at once.
- No experiment during an incident or a release.
