# Service virtualization recipe: Python

Common choices: `respx` (for `httpx`), `responses` (for `requests`), `pytest-httpserver` for a real local server, or WireMock in a container. Use what the project already has.

## respx with httpx

```python
import httpx, respx

@respx.mock(assert_all_called=True)
def test_payment_timeout_marks_order_pending(order_service, order_no):
    route = respx.post("https://payments.test/charges").mock(side_effect=httpx.ReadTimeout("timeout"))
    result = order_service.pay(order_no)
    assert result.status == "PAYMENT_PENDING"
    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content)["amount"] == "90.00"
```

- Error cases: `.mock(return_value=httpx.Response(503))`, a malformed body, `httpx.ConnectError`.

## responses with requests

```python
@responses.activate
def test_rate_limit():
    responses.post("https://payments.test/charges", status=429, json={"code": "RATE_LIMIT"})
    ...
```

## A real local server

`pytest-httpserver` starts a local HTTP server; point the client base URL to `httpserver.url_for("/")`. Use it when the code under test cannot use a patched client.
