# API testing recipe: TypeScript and JavaScript

Common choices: Playwright `request` (APIRequestContext), Supertest for an in-process app, or `fetch` with a test runner. Schema checks with a schema library (for example Zod or AJV). Use what the project already has.

## Playwright API test

```ts
import { test, expect } from '@playwright/test';
import { OrderSchema } from './schemas';

test('TC-007: create order returns 201, the order and a Location header', async ({ request }) => {
  const res = await request.post('/orders', {
    headers: await authHeaders('buyer'),          // project helper: fresh token
    data: { sku: `SKU-${crypto.randomUUID()}`, quantity: 2 },
  });
  expect(res.status()).toBe(201);
  expect(res.headers()['location']).toMatch(/^\/orders\/[0-9a-f-]{36}$/);
  const body = await res.json();
  const parsed = OrderSchema.safeParse(body);
  expect(parsed.success, JSON.stringify(parsed.error?.issues)).toBe(true);
  expect(body).toMatchObject({ quantity: 2, status: 'NEW' });
});
```

Set `baseURL` in the Playwright configuration from an environment variable.

## Supertest (in-process)

```ts
const res = await supertest(app).post('/orders').set(await authHeaders('buyer')).send(payload);
expect(res.status).toBe(201);
```

## Authorization cases

```ts
for (const [user, status] of [['anonymous', 401], ['viewer', 403], ['otherTenantBuyer', 404]] as const) {
  test(`cannot cancel another buyer's order as ${user}`, async ({ request }) => {
    const res = await request.post(`/orders/${orderOfBuyerA}/cancel`, { headers: await authHeaders(user) });
    expect(res.status()).toBe(status);
    expect(await orderStatus(orderOfBuyerA)).toBe('NEW');   // nothing changed
  });
}
```

## Pitfalls

- `res.ok()` is true for any 2xx. Check the exact status.
- Unawaited requests make the test end before the assertion.
- Do not share one authenticated context between roles in the same test file without care: cookies and tokens leak between cases.
