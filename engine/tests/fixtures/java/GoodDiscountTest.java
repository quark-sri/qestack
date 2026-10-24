package com.acme.order;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

@Tag("feature-003")
class DiscountTest {
    private final Discount d = new Discount();

    @Test @Tag("FR-001") @Tag("US1-AS1") @Tag("positive")
    @DisplayName("TC-001: 10% off at exactly 100.00")
    void discountAtThreshold() {
        assertEquals(90.0, d.apply(100.0), 0.001);
    }

    @Test @Tag("FR-001") @Tag("US1-AS2") @Tag("boundary")
    @DisplayName("TC-002: no discount at 99.99")
    void noDiscountBelow() {
        assertEquals(99.99, d.apply(99.99), 0.001);
    }

    @Test @Tag("FR-002") @Tag("EC-01") @Tag("negative") @Tag("error")
    @DisplayName("TC-003: negative total rejected with ORD-400")
    void negativeTotalOnlyNotNull() {
        var e = assertThrows(IllegalArgumentException.class, () -> d.apply(-0.01));
        assertEquals("ORD-400", e.getMessage());
    }
}
