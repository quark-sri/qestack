# API test checklist

## Effects to check for each call

| Effect | Check |
|---|---|
| Status | The exact code from the contract (`201`, not "2xx") |
| Body values | Each important field with the exact expected value |
| Body shape | Required fields, types, formats; no forbidden extra fields |
| Headers | `Content-Type`, `Location`, cache, rate limit, correlation ID, as the contract says |
| Error payload | Error code, message key, field errors; no stack trace and no personal data |
| Persisted state | The stored record, read through another path than the endpoint under test |
| Side effects | Messages published, calls to other services, emails, audit records |
| No side effect on failure | A rejected request changes nothing |

## Cases for each endpoint (when they apply)

- Missing required field; wrong type or format; value out of range (limit − 1, limit + 1)
- Unknown or extra field (when the contract rejects it)
- Mass assignment: the client sets a field it must not set (`id`, `status`, `price`, `role`)
- Not found; an ID of a deleted object
- Conflict: duplicate create, old version (`If-Match` / ETag → 412)
- Authentication missing or invalid → 401
- Authorization: wrong role → 403; another user's or tenant's object → 403 or 404, and no data in the body
- Idempotency: the same request twice; the same idempotency key with another body → 409 or 422
- Media type: unsupported `Content-Type` → 415; unsupported `Accept` → 406; body too large → 413
- Pagination, sorting, filters: first page, last page, page size limit, invalid sort field
- A downstream service is slow, fails or returns nonsense (simulated) → the status and error body from the contract

## GraphQL

- Errors come in the `errors` array, often with status 200. Check the array, not only the status.
- Check field-level authorization: a field that the role must not see.
- Check query depth and size limits.
