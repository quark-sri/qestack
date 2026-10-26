# Database test checklist

| Effect | Check |
|---|---|
| Round trip | Insert with all fields, read back through another path, compare all fields |
| Business key | Query by the business key, not only by count |
| No duplicates | The operation did not create extra rows |
| Constraints | Unique, foreign key, not null and check constraints reject bad data |
| Atomicity | A failure in a later step leaves no partial data |
| Partial update | An update changes only the intended columns |
| Delete | Delete or soft delete, and the effect on related rows (cascade, orphan, restrict) |
| Concurrency | Two updates with the same version: the second fails or waits, no lost update |
| Check-then-insert | Two requests that check "not exists" in code at the same time: one fails |
| Precision | Money columns keep scale and rounding; no float types for money |
| Time | Timestamps keep the time zone or are stored in UTC as the rule says |
| Text | Long values, other languages and special characters round trip unchanged |
| Ordering | Every query that the code expects in order has an `ORDER BY` |
| Pagination | Stable order with equal sort keys; no row lost or repeated between pages |
| Migrations | Up on existing data; the application reads old and new rows; down or a forward fix exists |
| Performance smell | A query in a loop (N+1) on a realistic data size |
