# Performance testing recipe: Java

Common choices: Gatling (Java or Scala DSL, Maven and Gradle plugins), Apache JMeter, or a JVM microbenchmark harness (JMH) for one method. Use what the project already has.

## Gatling simulation (Java DSL) with an open workload

```java
public class CheckoutSimulation extends Simulation {
    HttpProtocolBuilder http = http.baseUrl(System.getProperty("baseUrl")).acceptHeader("application/json");

    ScenarioBuilder checkout = scenario("checkout")
        .feed(csv("buyers.csv").circular())
        .exec(http("create order").post("/orders").body(ElFileBody("order.json")).asJson()
            .check(status().is(201), jsonPath("$.orderNo").saveAs("orderNo")))
        .pause(Duration.ofSeconds(2), Duration.ofSeconds(5))                    // think time
        .exec(http("pay").post("/orders/#{orderNo}/pay").check(status().is(200)));

    {
        setUp(checkout.injectOpen(
                rampUsersPerSec(1).to(50).during(Duration.ofMinutes(5)),          // ramp-up
                constantUsersPerSec(50).during(Duration.ofMinutes(15))))          // steady state
            .protocols(http)
            .assertions(
                global().responseTime().percentile(95.0).lt(400),
                global().failedRequests().percent().lt(1.0));
    }
}
```

Run with the Gatling Maven plugin (`mvn gatling:test -Dgatling.simulationClass=...`) or the Gradle plugin.

## JMH for one method

Use JMH only for a hot method in isolation. It does not replace a load test of the service.

## JVM metrics during the run

Watch heap and garbage collection pauses, thread pools, connection pool waits (for example through Micrometer metrics or JFR recordings).
