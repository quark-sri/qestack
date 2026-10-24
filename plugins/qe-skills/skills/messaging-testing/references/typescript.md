# Messaging testing recipe: TypeScript and JavaScript

Common choices: Testcontainers for Node (`@testcontainers/kafka` or a generic container), and the project's client library (for example KafkaJS). For waiting, use the test runner's polling or a small `waitFor` helper. Use what the project already has.

## A small wait helper (no fixed sleeps)

```ts
export async function waitFor<T>(check: () => Promise<T | undefined>, timeoutMs = 10_000, everyMs = 200): Promise<T> {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) {
    const v = await check();
    if (v !== undefined) return v;
    await new Promise((r) => setTimeout(r, everyMs));
  }
  throw new Error(`condition not met in ${timeoutMs} ms`);
}
```

## Producer test

```ts
const orderNo = `ORD-${crypto.randomUUID()}`;
const seen: Message[] = [];
await consumer.subscribe({ topic: 'orders', fromBeginning: true });          // unique groupId for each test
await consumer.run({ eachMessage: async ({ message }) => { if (message.key?.toString() === orderNo) seen.push(message); } });

await orderService.place(orderNo, items);
await waitFor(async () => (seen.length === 1 ? seen : undefined));
expect(JSON.parse(seen[0].value!.toString())).toMatchObject({ orderNo, total: '90.00' });
expect(seen[0].headers?.eventType?.toString()).toBe('OrderPlaced');
```

For transactional producers, configure the test consumer to read only committed messages (KafkaJS: `readUncommitted: false`, the default).

## Pitfalls

- Stop consumers and disconnect clients in `afterAll`, or the test runner hangs.
- Unique `groupId` for each test file; do not share one group.
- Decode with the contract schema, not with the producer's own types.
