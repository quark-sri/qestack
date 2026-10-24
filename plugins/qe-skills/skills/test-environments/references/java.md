# Test environment recipe: Java

Common choices: Testcontainers (JUnit 5 extension), Spring Boot service connections, Docker Compose for local stacks. Use what the project already has.

## Containers for a test class

```java
@Testcontainers
@SpringBootTest
class CheckoutIT {
    @Container @ServiceConnection
    static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16.4");     // pinned version

    @Container @ServiceConnection
    static KafkaContainer kafka = new KafkaContainer("apache/kafka:3.8.0");
}
```

Without Spring Boot service connections, use `@DynamicPropertySource` to pass `db.getJdbcUrl()` and the other values.

## Reuse and speed

- Static containers are shared by the tests of one class.
- A singleton container pattern (a static block in a base class) shares a container across classes in one JVM.
- Local reuse between runs (`testcontainers.reuse.enable=true`) is for developer machines only.

## Readiness

Use wait strategies such as `Wait.forHttp("/health").forStatusCode(200)` or `Wait.forLogMessage(".*started.*", 1)`.

## Pipeline

- The agent needs a container runtime. If it has none, the tests fail early with a clear message; do not skip them silently (`disabledWithoutDocker` hides the problem).
