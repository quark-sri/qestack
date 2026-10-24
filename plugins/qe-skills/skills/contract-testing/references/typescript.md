# Contract testing recipe: TypeScript and JavaScript

Common choice: Pact JS (`@pact-foundation/pact`) with a Pact Broker. Use what the project already has.

## Consumer test

```ts
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
const { like, regex } = MatchersV3;

const provider = new PactV3({ consumer: 'checkout-ui', provider: 'order-service' });

test('reads order ORD-1', async () => {
  provider
    .given('order ORD-1 exists')
    .uponReceiving('get order ORD-1')
    .withRequest({ method: 'GET', path: '/orders/ORD-1' })
    .willRespondWith({
      status: 200,
      body: { orderNo: 'ORD-1', total: like('90.00'), status: regex('NEW|PAID|CANCELLED', 'NEW') },
    });

  await provider.executeTest(async (mockServer) => {
    const order = await new OrderClient(mockServer.url).get('ORD-1');
    expect(order.status).toBe('NEW');
  });
});
```

## Provider verification

Use the Pact JS `Verifier` with the provider's base URL, the broker URL, the provider version and branch, and `stateHandlers` that create the data for each state. Run it in the provider's pipeline.

## Pipeline

- Publish pacts with the consumer version (the commit) and the branch.
- Run `can-i-deploy` before each deploy.

## Pitfalls

- Exact values in the body make the contract break on harmless changes. Use matchers.
- Keep provider states small and named after business facts ("order ORD-1 exists").
