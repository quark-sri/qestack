# Resilience testing recipe: TypeScript and JavaScript

Use what the project already has. Common choices: `msw` or `nock` for fake HTTP failures, Toxiproxy with its client for real connections, and fake timers for time.

## A fake dependency that fails or is slow

With `msw`:

```ts
import { http, HttpResponse, delay } from 'msw';

server.use(
  http.get('/rates', async () => { await delay(5_000); return HttpResponse.json({}); }), // slow
  http.get('/rates', () => HttpResponse.error()),                                        // network error
  http.get('/rates', () => new HttpResponse(null, { status: 503 })),                     // 503
);
```

Use `server.use` inside the test, and reset the handlers after each test.

## Timeouts and retries with fake timers

```ts
vi.useFakeTimers();
const result = getRates();                    // starts the call with a 2 s timeout
await vi.advanceTimersByTimeAsync(2_000);
await expect(result).rejects.toThrow(/timeout/i);
```

Count the calls to check the retry limit and the backoff times. Do not use a real sleep.

## Between real components

Use Toxiproxy between the service and its dependency. Add a latency toxic, check the behavior, remove it, and check that the service recovers.
