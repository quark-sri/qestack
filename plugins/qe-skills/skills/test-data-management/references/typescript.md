# Test data recipe: TypeScript and JavaScript

Common choices: small factory functions, a factory library (for example Fishery), Faker (`@faker-js/faker`) with a seed. Use what the project already has.

## Factory with valid defaults and unique keys

```ts
let seq = 0;
export function anOrder(overrides: Partial<Order> = {}): Order {
  seq += 1;
  return {
    orderNo: `ORD-${seq}-${crypto.randomUUID().slice(0, 8)}`,
    total: '50.00',
    status: 'NEW',
    customer: aCustomer(),
    ...overrides,                       // the test shows only what matters
  };
}

const order = anOrder({ total: '100.00' });
```

## Realistic values with a seed

```ts
import { faker } from '@faker-js/faker';
faker.seed(42);                         // log the seed when a test fails
const email = `user+${crypto.randomUUID()}@example.test`;
```

## Persisting

- End-to-end and API tests: create through the API (`await api.post('/orders', { data: anOrder() })`).
- Integration tests: insert through the repository or the query builder.
- Use a Playwright fixture or a `beforeEach` that creates the data and an `afterEach` that removes it.
