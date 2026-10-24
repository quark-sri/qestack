# Edge case catalog

Use the sections that match the inputs, states and dependencies of the target. Each line is a question to ask about the target.

## Numbers

- Zero, one, minus one. The smallest and the largest allowed value.
- Exactly at each limit, one step below and one step above. The step comes from the type: 1 for integers, 0.01 for money with two decimals.
- Negative values where only positive values make sense.
- Overflow: the largest value plus one, a sum or product of large values.
- Floating point: 0.1 + 0.2, rounding mode (half up, half even), many decimals.
- Not a number, infinity, a number as text ("10"), a number with spaces or a thousands separator.

## Text

- Empty, only spaces, null or missing.
- One character. Exactly the maximum length, and one more.
- Leading and trailing spaces. Upper and lower case ("Admin" and "admin").
- Unicode: accents, combined characters, right-to-left text, emoji, characters outside the basic plane.
- Special characters: quotes, backslash, `<script>`, `%`, `_`, `'; --`, path parts such as `../`.
- Line breaks, tabs, zero-width characters.
- Another encoding than the system expects.

## Dates and time

- Today, yesterday, tomorrow. A date in the past where only the future is allowed, and the reverse.
- End of the month, 29 February, end of the year, the year change.
- Daylight saving changes: the hour that does not exist, the hour that exists twice.
- Time zones: the user, the server and the database in different zones. Midnight UTC is another day elsewhere.
- Start equals end. End before start. A very long range.
- Expiry exactly now. A token or session that expires during the operation.

## Money

- Currency missing or different. Exchange rate changes.
- Rounding of each line compared with rounding of the total.
- Discounts that make the total zero or negative. Refunds larger than the payment.
- Tax rules at the limits.

## Collections and lists

- Empty, one element, the maximum number, one more than the maximum.
- Duplicates. Null elements. Mixed types.
- Order: sorted, reverse, random. Stable sort with equal keys.
- Pagination: first page, last page, a page after the end, page size 0, a very large page size, data that changes between pages.

## Identifiers and references

- Unknown ID. An ID of a deleted object. An ID that belongs to another user or tenant.
- An ID in the wrong format. A very long ID.
- A reference that points to itself, or a cycle.

## Files and payloads

- Empty file. A very large file. A wrong file type with the right extension.
- A file name with spaces, unicode or path parts.
- Missing required field. An extra unknown field. A field with the wrong type. Deep nesting.
- Malformed payload, truncated payload.

## State and workflow

- Each action in each state, also the states where it is not allowed.
- The same action twice (double click, retry, duplicate message).
- An action on an object that another user just changed or deleted.
- Steps out of order, a skipped step, a step after a cancel.

## Concurrency

- Two requests at the same time for the same object. Last write wins, or a conflict error?
- Two requests at the same time that both check a limit ("only 1 left").
- A long operation with a timeout in the middle.

## Users and security

- No user, an expired session, a user with the wrong role, a user of another tenant.
- A user who changes an ID in the request to reach another user's data.
- Input that the client must not set (owner, price, status, role).
- Error messages that show internal details or personal data.

## Integrations and failures

- The dependency is slow, returns an error, returns an unexpected format, or does not answer.
- The dependency succeeds, but the next step fails. Is the first step undone?
- A message arrives twice, out of order, or after a long delay.
- The dependency is not available at startup.

## Configuration and environment

- A missing or empty setting. A feature flag on and off.
- Another locale: decimal comma, date format, sort order of letters.
- Low disk space, no network, a read-only file system.
