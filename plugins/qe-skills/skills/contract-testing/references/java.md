# Contract testing recipe: Java

Common choices: Pact JVM (consumer-driven, with a Pact Broker), or Spring Cloud Contract (provider-driven, common in Spring teams). For events: a schema registry compatibility check, or Pact message contracts. Use what the project already has.

## Pact JVM consumer test (JUnit 5)

Check the exact class and method names for the Pact JVM version in the project; the DSL changed between major versions.

```java
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "order-service")
class OrderClientPactTest {

    @Pact(consumer = "checkout-ui")
    V4Pact orderExists(PactDslWithProvider builder) {
        return builder
            .given("order ORD-1 exists")                              // provider state
            .uponReceiving("get order ORD-1")
                .path("/orders/ORD-1").method("GET")
            .willRespondWith()
                .status(200)
                .body(new PactDslJsonBody()
                    .stringValue("orderNo", "ORD-1")                    // the consumer depends on this value
                    .decimalType("total")                               // type only
                    .stringMatcher("status", "NEW|PAID|CANCELLED", "NEW"))
            .toPact(V4Pact.class);
    }

    @Test
    void readsTheOrder(MockServer server) {
        var order = new OrderClient(server.getUrl()).get("ORD-1");
        assertThat(order.status()).isEqualTo("NEW");
    }
}
```

## Provider verification

Use the Pact JVM provider JUnit 5 support with `@Provider("order-service")`, a broker source, and a `@State("order ORD-1 exists")` method that creates the data. Run it in the provider's pipeline.

## Pipeline

- Publish consumer pacts with the consumer version (the commit) and the branch.
- Run `can-i-deploy` (Pact Broker CLI) before each deploy, for the version and the target environment.

## Events

- With a schema registry: set the compatibility mode for each subject (for example BACKWARD). Test new schemas against it in the pipeline, with the registry's Maven or Gradle plugin, or its REST API.
