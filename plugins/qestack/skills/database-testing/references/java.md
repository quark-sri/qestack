# Database testing recipe: Java

Common choices: Testcontainers for the database engine, JUnit 5, AssertJ. With Spring: `@DataJpaTest` or `@SpringBootTest` plus Testcontainers. Migrations with Flyway or Liquibase. Use what the project already has.

## Real engine in a container

```java
@Testcontainers
class OrderRepositoryIT {
    @Container
    static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");   // same major version as production
    // Spring Boot: @ServiceConnection on the field, or @DynamicPropertySource for the URL, user and password
}
```

- Name the class `*IT` when the build runs integration tests with Failsafe.
- Tag it (`@Tag("integration")`) so that fast pipelines can skip it and mutation tools can exclude it.

## Read back through another path

```java
orders.save(order);
entityManager.flush();
entityManager.clear();                         // the first-level cache no longer returns the saved object
Map<String, Object> row = jdbc.queryForMap("select total, status from orders where order_no = ?", order.getNo());
assertThat((BigDecimal) row.get("total")).isEqualByComparingTo("90.00");
```

## Commit behavior

- Spring tests with `@Transactional` roll back at the end. They do not see commit-time constraint violations, and `@TransactionalEventListener(AFTER_COMMIT)` and outbox relays do not run. For those tests, remove the test transaction and clean up by truncation.

## Lost update

```java
var a = repo.findById(id).orElseThrow();
var b = repo.findById(id).orElseThrow();
a.setQuantity(1); repo.saveAndFlush(a);
b.setQuantity(2);
assertThatThrownBy(() -> repo.saveAndFlush(b)).isInstanceOf(ObjectOptimisticLockingFailureException.class);
```

## Migrations

Start the container, apply the migrations up to the version before the change, insert old-shape rows with JDBC, run the remaining migrations, then check the data.
