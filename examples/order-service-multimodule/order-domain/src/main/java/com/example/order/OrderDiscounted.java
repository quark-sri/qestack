package com.example.order;

import java.math.BigDecimal;

/** FR-003: the event key is the order ID. */
public record OrderDiscounted(String key, BigDecimal total) {
}
