package com.example.order;

/** Publishes domain events. In production this is a message broker client. */
public interface EventPublisher {
    void publish(OrderDiscounted event);
}
