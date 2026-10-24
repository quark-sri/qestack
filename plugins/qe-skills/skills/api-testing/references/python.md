# API testing recipe: Python

Common choices: pytest with `httpx` or `requests`. In-process: the framework's test client (for example the FastAPI or Flask test client). Schema checks with `jsonschema` or the project's models. Use what the project already has.

## Test with shape and values

```python
def test_create_order_returns_201_and_location(api, auth_headers, order_schema):
    res = api.post("/orders", headers=auth_headers("buyer"),
                   json={"sku": f"SKU-{uuid.uuid4()}", "quantity": 2})
    assert res.status_code == 201
    assert re.fullmatch(r"/orders/[0-9a-f-]{36}", res.headers["location"])
    body = res.json()
    jsonschema.validate(body, order_schema)
    assert body["quantity"] == 2
    assert body["status"] == "NEW"
```

`api` is a fixture with an `httpx.Client(base_url=os.environ["API_BASE_URL"], timeout=10)`.

## Authorization cases

```python
@pytest.mark.parametrize(("user", "status"), [("anonymous", 401), ("viewer", 403), ("other_tenant_buyer", 404)])
def test_cannot_cancel_someone_elses_order(api, auth_headers, order_of_buyer_a, user, status):
    res = api.post(f"/orders/{order_of_buyer_a}/cancel", headers=auth_headers(user))
    assert res.status_code == status
    assert order_status(order_of_buyer_a) == "NEW"   # nothing changed
```

## Contract-driven checks

If an API description file exists, a property-based tool such as Schemathesis can send generated requests and check the responses against the description. Use it in addition to the explicit value checks, not instead of them.

## Pitfalls

- `res.ok` is true for any status below 400. Check the exact code.
- Do not disable TLS checks in shared test code without a reason.
- Session-scoped clients keep cookies between tests. Use a new client per role.
