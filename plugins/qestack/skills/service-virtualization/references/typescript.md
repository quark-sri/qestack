# Service virtualization recipe: TypeScript and JavaScript

Common choices: MSW (Mock Service Worker) for Node and the browser, `nock` for Node HTTP, Playwright `page.route` for browser calls, or WireMock in a container. Use what the project already has.

## MSW in Node tests

```ts
import { http, HttpResponse, delay } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer();
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));   // an unexpected call fails the test
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('payment timeout marks the order pending', async () => {
  let charged = 0;
  server.use(http.post('https://payments.test/charges', async () => {
    charged++;
    await delay(5_000);                                           // longer than the client timeout
    return HttpResponse.json({ id: 'ch_1' });
  }));
  const result = await orderService.pay(orderNo);
  expect(result.status).toBe('PAYMENT_PENDING');
  expect(charged).toBe(1);
});
```

- Error cases: `HttpResponse.json({ code: 'RATE_LIMIT' }, { status: 429 })`, `HttpResponse.error()` for a network error.

## Browser calls

`await page.route('**/payments/**', (route) => route.fulfill({ status: 503, body: '' }));` simulates a failing dependency of the frontend.
