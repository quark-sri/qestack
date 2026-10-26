# Test data recipe: Java

Common choices: hand-written builders (or Lombok `@Builder`), Instancio or a similar object generator, Datafaker for realistic values, Testcontainers for databases. Use what the project already has.

## Builder with valid defaults and unique keys

```java
public final class OrderBuilder {
    private static final AtomicLong SEQ = new AtomicLong();
    private String orderNo = "ORD-" + SEQ.incrementAndGet() + "-" + UUID.randomUUID().toString().substring(0, 8);
    private BigDecimal total = new BigDecimal("50.00");
    private Status status = Status.NEW;
    private Customer customer = CustomerBuilder.aCustomer().build();

    public static OrderBuilder anOrder() { return new OrderBuilder(); }
    public OrderBuilder withTotal(String total) { this.total = new BigDecimal(total); return this; }
    public OrderBuilder paid() { this.status = Status.PAID; return this; }
    public Order build() { return new Order(orderNo, total, status, customer); }
}

// In the test, only the value that matters is visible:
Order order = anOrder().withTotal("100.00").build();
```

## Realistic values with a seed

```java
Faker faker = new Faker(new Random(42));      // Datafaker; log the seed when a test fails
String email = "user+" + UUID.randomUUID() + "@example.test";
```

## Persisting

- API tests: create through the API client helper (`api.createOrder(anOrder().paid().build())`).
- Integration tests: save through the repository, or insert with JDBC for speed.
- Clean up with truncation after each test class, or use a schema for each test class.
