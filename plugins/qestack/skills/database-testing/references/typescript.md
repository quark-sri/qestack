# Database testing recipe: TypeScript and JavaScript

Common choices: Testcontainers for Node, the project's ORM or query builder (for example Prisma, TypeORM, Knex, Drizzle), and its migration tool. Use what the project already has.

## Real engine in a container

```ts
import { PostgreSqlContainer, StartedPostgreSqlContainer } from '@testcontainers/postgresql';

let db: StartedPostgreSqlContainer;
beforeAll(async () => {
  db = await new PostgreSqlContainer('postgres:16').start();     // same major version as production
  process.env.DATABASE_URL = db.getConnectionUri();
  await runMigrations();                                          // the project's migration command
}, 120_000);
afterAll(async () => { await db.stop(); });
```

## Read back through another path

Read with a plain SQL query (`pool.query(...)` or the driver), not with the repository method under test.

```ts
const { rows } = await pool.query('select total, status from orders where order_no = $1', [orderNo]);
expect(rows[0]).toEqual({ total: '90.00', status: 'NEW' });   // numeric columns often come back as strings
```

## Concurrency

Run two operations with `Promise.all` on two connections, and check that exactly one wins, or that the version check rejects the second.

## Pitfalls

- An ORM with a different dialect in tests (for example a file database) hides real query and type errors.
- JavaScript numbers lose precision for large integers and money. Compare decimal values as strings or with a decimal library.
- Truncate tables between test files, or use a schema for each worker when tests run in parallel.
