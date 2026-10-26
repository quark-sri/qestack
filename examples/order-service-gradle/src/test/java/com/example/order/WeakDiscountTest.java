package com.example.order;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/**
 * Typical weak AI-written tests. They are green, and they look complete: each requirement
 * has a test. But most of them cannot fail when the product is wrong. qestack shows why.
 */
@Tag("feature-001")
class WeakDiscountTest {

    private final List<OrderDiscounted> published = new ArrayList<>();
    private final OrderService service = new OrderService(published::add);

    @Test
    @Tag("FR-001") @Tag("positive")
    void discountIsCalculated() {
        // not-null only: any total passes
        assertNotNull(service.checkout("ORD-1", new BigDecimal("100.00")));
    }

    @Test
    @Tag("FR-001") @Tag("boundary")
    void boundaryValues() {
        // hollow: written later
    }

    @Test
    @Tag("FR-002") @Tag("negative")
    void negativeTotalIsRejected() {
        // type only: the error code ORD-400 is not checked
        assertThrows(OrderException.class, () -> service.checkout("ORD-2", new BigDecimal("-1.00")));
    }

    @Test
    @Tag("FR-003") @Tag("positive")
    void eventIsPublished() {
        service.checkout("ORD-3", new BigDecimal("150.00"));
        // size only: the key and the total are not checked
        assertThat(published).hasSize(1);
    }

    @Disabled("flaky")
    @Test
    @Tag("FR-003") @Tag("negative")
    void noEventBelowTheLimit() {
        service.checkout("ORD-4", new BigDecimal("99.99"));
        assertThat(published).isEmpty();
    }
}
