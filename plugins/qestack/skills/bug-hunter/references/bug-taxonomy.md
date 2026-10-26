# Bug taxonomy

Ask each question for each entry point of the target.

## Logic

- Is a comparison off by one (`<` instead of `<=`)? Is a limit included or not?
- Is a condition inverted, or are `and` and `or` mixed up?
- Does a branch miss a case (a status, an enum value, a type)? What happens in the default branch?
- Is the order of operations wrong (validate after save, check after use)?
- Does an early return skip a needed step (cleanup, audit, event)?

## Null, empty and missing

- What happens with null, an empty string, an empty list, a missing key, a missing file?
- Does the code use a value before it checks it?
- Does an optional value get a wrong default?

## Numbers and data

- Integer overflow, division by zero, floating point for money, wrong rounding mode.
- Wrong unit (seconds and milliseconds, cents and units, bytes and kilobytes).
- Lost precision in a conversion, or truncation of text.
- Wrong mapping between two models: fields swapped, a field not copied, a wrong default.
- Wrong encoding or case handling in comparisons.

## Errors

- Is an exception or an error result ignored, logged only, or turned into success?
- Does the error message or code match the contract?
- After an error, is the state consistent? Is a partial change undone?
- Is the error too broad (catch everything) or does it hide the cause?
- Is a retry safe, or does it repeat a side effect?

## State and life cycle

- Can an action run in a state where it is not allowed?
- Is the state saved before an external call that can fail?
- Does a cache return stale data after an update?
- Is a resource (connection, file, lock, subscription) closed on every path?

## Concurrency

- Check-then-act: two requests pass the check at the same time.
- Shared mutable data without protection.
- Lost update: two writers, the last one wins without a version check.
- Order of asynchronous events that is not guaranteed.
- A timeout that leaves work half done.

## Time

- Time zone of "today". Daylight saving. End of month. Leap year.
- A call to the system clock that makes the result change from run to run.
- Expiry checks with the wrong comparison.

## Security

- A missing permission check, or a check on the wrong object (another user's ID).
- Input that reaches a query, a command, a path or a page without escaping.
- Secrets or personal data in logs, errors or responses.
- A client-controlled field that the server trusts (price, role, owner).

## Integration

- A wrong assumption about the other system: format, units, optional fields, error codes.
- No timeout, no retry limit, or a retry storm.
- A message sent before the data is committed, or not sent after a rollback.
- Duplicate or out-of-order messages.

## Configuration

- A default that is right for development and wrong for production.
- A feature flag path that nobody tests.
- A setting read once at startup and never updated.
