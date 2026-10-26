package com.example.order;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** FR-001: 10% off when the total is 100.00 or more, rounded half up to two decimals. */
public final class Discount {

    static final BigDecimal LIMIT = new BigDecimal("100.00");
    private static final BigDecimal FACTOR = new BigDecimal("0.90");

    public boolean appliesTo(BigDecimal total) {
        return total.compareTo(LIMIT) >= 0;
    }

    public BigDecimal apply(BigDecimal total) {
        BigDecimal result = appliesTo(total) ? total.multiply(FACTOR) : total;
        return result.setScale(2, RoundingMode.HALF_UP);
    }
}
