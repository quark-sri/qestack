# Messaging testing recipe: Python

Common choices: pytest, `testcontainers` for the broker, the project's client (for example `confluent-kafka`), and a small polling helper. Use what the project already has.

## Test consumer

```python
consumer = Consumer({
    "bootstrap.servers": kafka.get_bootstrap_server(),
    "group.id": f"test-{uuid.uuid4()}",          # unique group for each test
    "auto.offset.reset": "earliest",
    "isolation.level": "read_committed",          # no events from rolled-back transactions
})
consumer.subscribe(["orders"])
```

## Producer test with polling

```python
def poll_for(consumer, key, timeout=10.0):
    found, end = [], time.monotonic() + timeout
    while time.monotonic() < end and not found:
        msg = consumer.poll(0.2)
        if msg is not None and msg.error() is None and msg.key() == key.encode():
            found.append(msg)
    return found

def test_place_order_publishes_one_event(order_service, consumer):
    order_no = f"ORD-{uuid.uuid4()}"
    order_service.place(order_no, items)
    msgs = poll_for(consumer, order_no)
    assert len(msgs) == 1
    assert json.loads(msgs[0].value())["total"] == "90.00"
    assert dict(msgs[0].headers())["eventType"] == b"OrderPlaced"
    assert poll_for(consumer, order_no, timeout=2.0) == []    # no duplicate
```

## Pitfalls

- Close consumers in a fixture finalizer.
- Do not use `time.sleep` as the wait. Poll for the condition.
- Decode with the contract schema (for example the Avro or JSON schema), not with the producer's classes.
