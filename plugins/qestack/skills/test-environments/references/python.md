# Test environment recipe: Python

Common choices: `testcontainers` for Python, Docker Compose, pytest session fixtures. Use what the project already has.

## Session fixture with a container

```python
@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16.4") as pg:      # pinned version
        os.environ["DATABASE_URL"] = pg.get_connection_url()
        yield pg
```

## Parallel workers (pytest-xdist)

Use the `worker_id` fixture to give each worker its own database or schema name:

```python
@pytest.fixture(scope="session")
def schema_name(worker_id):
    return f"test_{worker_id}"
```

## Compose

Pin image versions, add health checks, and start with `docker compose up --wait`.
