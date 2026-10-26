# Resilience testing recipe: Java

Use what the project already has. Common choices: Toxiproxy (with the Testcontainers module) to inject latency and cuts between real components, WireMock fault and delay stubs, and the test support of Resilience4j.

## A fake dependency that fails or is slow (unit and component level)

With WireMock:

```java
stubFor(get("/rates").willReturn(aResponse().withFixedDelay(5_000).withStatus(200)));   // slow
stubFor(get("/rates").willReturn(aResponse().withFault(Fault.CONNECTION_RESET_BY_PEER))); // cut
stubFor(get("/rates").willReturn(serverError()));                                        // 500
```

Assert the behavior, not only "no exception": the timeout fires near the configured value, the fallback value is returned, and the retry count is as configured. Check the number of calls with `verify(exactly(3), getRequestedFor(urlEqualTo("/rates")))`.

## Between real components

Toxiproxy sits between the service and the database or the broker. Add a latency toxic or cut the connection, check the behavior, then remove the toxic and check the recovery. Wait with a condition (Awaitility), not with a fixed sleep.

## Retries and breakers

Test the configuration as behavior: a call that always fails opens the breaker after the set number of calls, and a later success closes it. Control the clock or the wait time through the configuration of the test, not with a real sleep.
