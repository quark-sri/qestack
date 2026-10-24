# Messaging testing recipe: Java

Common choices: Testcontainers for Kafka (or another broker), the Kafka client or Spring for Apache Kafka, Awaitility for waiting, AssertJ. Use what the project already has.

## Broker in a container

```java
@Container
static KafkaContainer kafka = new KafkaContainer("apache/kafka:3.8.0");   // org.testcontainers.kafka.KafkaContainer
// Spring Boot: @ServiceConnection on the field, or set spring.kafka.bootstrap-servers from kafka.getBootstrapServers()
```

## A test consumer that does not miss or leak events

```java
Properties p = new Properties();
p.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapServers());
p.put(ConsumerConfig.GROUP_ID_CONFIG, "test-" + UUID.randomUUID());   // unique group for each test
p.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
p.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");       // no events from rolled-back transactions
```

## Producer test: exactly one event, key, value, headers

```java
String orderNo = "ORD-" + UUID.randomUUID();
orderService.place(orderNo, items);

List<ConsumerRecord<String, OrderPlaced>> records = new ArrayList<>();
await().atMost(Duration.ofSeconds(10)).untilAsserted(() -> {
    consumer.poll(Duration.ofMillis(200)).forEach(r -> { if (orderNo.equals(r.key())) records.add(r); });
    assertThat(records).hasSize(1);
});
ConsumerRecord<String, OrderPlaced> r = records.get(0);
assertThat(r.value().total()).isEqualByComparingTo("90.00");
assertThat(new String(r.headers().lastHeader("eventType").value(), UTF_8)).isEqualTo("OrderPlaced");
```

Then poll once more for a short time and check that `records` still has one element (no duplicate).

## Consumer test: idempotency

Publish the same record twice (same key and event ID). Wait until the state shows the first one. Then check that the state after the second one is equal.

## Dead-letter test

Publish a record that cannot be decoded. Wait for the record on the dead-letter topic, check its headers (original topic, exception), and check that a valid record after it is still processed.

## Pitfalls

- An embedded broker is acceptable for fast tests only if the team accepts the differences.
- Tag broker tests `integration`, so that fast pipelines and mutation tools can skip them.
