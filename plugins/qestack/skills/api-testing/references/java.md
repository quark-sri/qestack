# API testing recipe: Java

Common choices: REST Assured, the JDK `HttpClient` with a JSON library, or the team's internal client library. For in-process tests in Spring: MockMvc or WebTestClient. Use what the project already has.

## REST Assured test with shape and values

```java
@Test
@DisplayName("TC-007: create order returns 201, the order and a Location header")
void createOrder() {
    given()
        .spec(authenticatedAs("buyer"))          // project helper: fresh token, base URI, logging on failure
        .contentType(ContentType.JSON)
        .body(Map.of("sku", "SKU-" + UUID.randomUUID(), "quantity", 2))
    .when()
        .post("/orders")
    .then()
        .statusCode(201)
        .header("Location", matchesPattern("/orders/[0-9a-f-]{36}"))
        .body(matchesJsonSchemaInClasspath("schemas/order.json"))   // json-schema-validator module
        .body("quantity", equalTo(2))
        .body("status", equalTo("NEW"));
}
```

- Validate against an API description file with a request/response validator library (for example the Atlassian swagger-request-validator filter for REST Assured).
- Log the request and the response only on failure: `.log().ifValidationFails()`.

## JDK HttpClient or an internal library

- Wrap the client in a small test helper that adds authentication, sets timeouts and parses JSON.
- Name the helper's assertion methods `assert...` or `verify...` so that reviewers and linters see them.
- If the library has a "check status" helper, also check the body. Status alone is shallow.

## Persisted state

Read the stored state through another path: a repository or JDBC query in the test, or a follow-up GET. Do not use the endpoint under test to prove its own write.

## Authorization cases

```java
@ParameterizedTest
@CsvSource({"anonymous, 401", "viewer, 403", "other-tenant-buyer, 404"})
void cannotCancelSomeoneElsesOrder(String user, int status) {
    given().spec(authenticatedAs(user)).when().post("/orders/{id}/cancel", orderOfBuyerA)
        .then().statusCode(status);
    assertThat(orderStatus(orderOfBuyerA)).isEqualTo("NEW");   // nothing changed
}
```

## Run

- Unit-like API tests with an in-process server run with the normal test command.
- Tests against a running environment usually run as integration tests (for example a Failsafe `*IT` class, or a Gradle task). They take the base URI from a system property or an environment variable.
