# Security test checklist

| Area | Tests |
|---|---|
| Authentication | Wrong password, locked account, expired and revoked tokens, a token signed with another key or with no signature, password reset flow abuse, brute force limits |
| Sessions | Logout invalidates the session on the server; session fixation; cookie flags (`Secure`, `HttpOnly`, `SameSite`) |
| Authorization | Each role for each action; another user's or tenant's object ID (direct object reference); admin-only functions; changing a role or an owner through the request |
| Mass assignment | Fields the client must not set: `id`, `role`, `owner`, `price`, `status` |
| Injection | SQL, NoSQL, command, template, LDAP, path traversal (`../`), header injection, in every input that reaches such a sink |
| Cross-site scripting | Stored and reflected input shown in pages; output encoding; content security policy |
| Cross-site request forgery | State-changing requests without a valid token or with a foreign origin (for cookie-based sessions) |
| Sensitive data | No secrets, tokens or personal data in responses, errors, logs, URLs or caches; masking where needed |
| Transport and headers | HTTPS only; `Strict-Transport-Security`; no server version banners; CORS allows only known origins |
| Rate limits | Login, password reset, expensive searches, message sending |
| File upload | Type checks by content, size limits, file names with paths, files that run code |
| Server-side request forgery | A URL input that makes the server call internal addresses |
| Business logic | Negative quantities, coupon reuse, skipped workflow steps, race conditions on limited stock or balance |
| Dependencies | Known vulnerable libraries (a dependency scan in the pipeline) |
| Secrets | No credentials in the repository or in the build output (a secret scan in the pipeline) |
| Configuration | Debug endpoints, default accounts, open admin consoles, verbose errors in non-development environments |
