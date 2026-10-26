# Test environment recipe: TypeScript and JavaScript

Common choices: Testcontainers for Node, Docker Compose, the test runner's global setup. Use what the project already has.

## Global setup with containers

```ts
// vitest.global-setup.ts (or Jest globalSetup)
import { PostgreSqlContainer } from '@testcontainers/postgresql';

export default async function setup() {
  const db = await new PostgreSqlContainer('postgres:16.4').start();   // pinned version
  process.env.DATABASE_URL = db.getConnectionUri();
  return async () => { await db.stop(); };                          // teardown
}
```

## Compose for a local stack

- Pin image versions in `compose.yaml`, and add `healthcheck` entries.
- Start with `docker compose up --wait`, so that the command returns only when the services are healthy.

## Parallel workers

Use the worker ID (`process.env.VITEST_POOL_ID` or `process.env.JEST_WORKER_ID`) to give each worker its own schema, database name or key prefix.

## Playwright

Use `webServer` in the Playwright configuration to start the application and wait for its URL before the tests run.
