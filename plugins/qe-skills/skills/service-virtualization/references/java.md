# Service virtualization recipe: Java

Common choices: WireMock (in process with the JUnit 5 extension, or as a container), MockServer, or an in-process fake class for unit tests. Use what the project already has.

## WireMock with JUnit 5

```java
@RegisterExtension
static WireMockExtension payments = WireMockExtension.newInstance()
    .options(wireMockConfig().dynamicPort()).build();

@Test
void paymentTimeoutMarksOrderPending() {
    payments.stubFor(post(urlEqualTo("/charges"))
        .willReturn(aResponse().withStatus(200).withFixedDelay(5_000)));   // longer than the client timeout

    var result = orderService.pay(orderNo);                                 // client base URL = payments.baseUrl()

    assertThat(result.status()).isEqualTo("PAYMENT_PENDING");
    payments.verify(1, postRequestedFor(urlEqualTo("/charges"))
        .withRequestBody(matchingJsonPath("$.amount", equalTo("90.00"))));
}
```

- Error cases: `aResponse().withStatus(503)`, `.withFault(Fault.CONNECTION_RESET_BY_PEER)`, a malformed body.
- Stateful flows: WireMock scenarios (`inScenario(...).whenScenarioStateIs(...)`).
- Configure the client's base URL from a property, so the test can point it to `payments.baseUrl()`.

## Recording

Record real sandbox traffic once with the WireMock recorder, review it, remove secrets, and keep the mappings in the repository.
