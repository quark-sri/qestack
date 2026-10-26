package com.example.order;

import java.math.BigDecimal;

/** Checkout: FR-001 (discount), FR-002 (reject negative totals), FR-003 (OrderDiscounted event). */
public final class OrderService {

    private final Discount discount = new Discount();
    private final EventPublisher events;

    public OrderService(EventPublisher events) {
        this.events = events;
    }

    public BigDecimal checkout(String orderId, BigDecimal total) {
        if (total.signum() < 0) {
            throw new OrderException("ORD-400", "negative total for " + orderId);
        }
        BigDecimal result = discount.apply(total);
        if (discount.appliesTo(total)) {
            events.publish(new OrderDiscounted(orderId, result));
        }
        return result;
    }
}
