# Resilience testing recipe: Python

Use what the project already has. Common choices: `responses` or `respx` or `pytest-httpserver` for fake HTTP failures, and Toxiproxy for real connections. Use `freezegun` or an injected clock for time.

## A fake dependency that fails or is slow

With `respx` (for `httpx`):

```python
import httpx, respx

with respx.mock:
    respx.get("https://rates.test/rates").mock(side_effect=httpx.ConnectTimeout("slow"))   # timeout
    respx.get("https://rates.test/rates").mock(return_value=httpx.Response(503))           # 503
```

For a sequence (fail twice, then succeed), pass a list to `side_effect`, then assert the number of calls and the final result:

```python
route = respx.get("https://rates.test/rates").mock(
    side_effect=[httpx.Response(503), httpx.Response(503), httpx.Response(200, json={"eur": 1.1})])
assert get_rates() == {"eur": 1.1}
assert route.call_count == 3
```

## Timeouts

Pass a short timeout in the test configuration and assert that the call stops near it. Do not wait for the production value.

## Between real components

Use Toxiproxy between the service and its dependency: add latency, check the behavior, remove it, and check the recovery. Wait for a condition, not a fixed sleep.
