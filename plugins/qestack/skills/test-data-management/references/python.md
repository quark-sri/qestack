# Test data recipe: Python

Common choices: `factory_boy`, Faker with a seed, pytest fixtures, or plain builder functions. Use what the project already has.

## Factory with valid defaults and unique keys

```python
class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    order_no = factory.Sequence(lambda n: f"ORD-{n}-{uuid.uuid4().hex[:8]}")
    total = Decimal("50.00")
    status = "NEW"
    customer = factory.SubFactory(CustomerFactory)

    class Params:
        paid = factory.Trait(status="PAID")

order = OrderFactory(total=Decimal("100.00"))      # only the value that matters is visible
paid_order = OrderFactory(paid=True)
```

With an ORM, use the ORM factory base class (for example `factory.alchemy.SQLAlchemyModelFactory` or `factory.django.DjangoModelFactory`).

## Realistic values with a seed

```python
Faker.seed(42)                                      # log the seed when a test fails
email = f"user+{uuid.uuid4()}@example.test"
```

## Fixtures

Use function-scoped fixtures for data that tests change. Use session-scoped fixtures only for read-only reference data.
