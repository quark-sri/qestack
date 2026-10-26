# Database testing recipe: Python

Common choices: pytest, `testcontainers` for Python, the project's ORM (for example SQLAlchemy or the Django ORM) and its migration tool (for example Alembic or Django migrations). Use what the project already has.

## Real engine in a container

```python
@pytest.fixture(scope="session")
def database_url():
    with PostgresContainer("postgres:16") as pg:          # same major version as production
        url = pg.get_connection_url()
        run_migrations(url)                                # the project's migration command
        yield url
```

## Read back through another path

```python
session.add(order)
session.commit()
session.expire_all()                                       # do not reuse the cached object
row = engine.connect().execute(text("select total, status from orders where order_no = :n"), {"n": order.no}).one()
assert row.total == Decimal("90.00")
```

## Commit behavior

A test that wraps each case in a transaction and rolls back does not see commit-time constraints or after-commit hooks. For those tests, commit for real and clean up with truncation.

## Django

`TestCase` wraps each test in a transaction. Use `TransactionTestCase` (or `pytest.mark.django_db(transaction=True)`) when the test needs real commits, for example for `on_commit` hooks.

## Pitfalls

- A file database in tests and another engine in production: types, constraints and locking differ.
- `float` columns for money. Use `Numeric` and `Decimal`.
- Session-scoped data fixtures shared between tests that change the data.
