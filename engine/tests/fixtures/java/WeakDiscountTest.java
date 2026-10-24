package com.acme.order;

import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;
import static org.assertj.core.api.Assertions.assertThat;

@Tag("feature-003")
@DisplayName("Discount rules { not a brace }")
class DiscountTest {

    private final Discount d = new Discount();

    @Test
    @Tag("FR-001") @Tag("US1-AS1") @Tag("positive")
    @DisplayName("TC-001: 10% off at 100")
    void discountAtThreshold() {
        assertEquals(90.0, d.apply(100.0), 0.001);
    }

    @Tag("FR-001") @Tag("boundary")
    @ParameterizedTest(name = "total {0}")
    @ValueSource(doubles = {99.99, 50})
    void noDiscountBelow(double total) {
        assertThat(d.apply(total)).isEqualTo(total);
    }

    @Test
    @Tag("FR-002")
    void hollowTest() {
        // TODO write this
    }

    @Test @Tag("FR-002") @Tag("negative")
    void negativeTotalOnlyNotNull() {
        var e = assertThrows(IllegalArgumentException.class, () -> d.apply(-1));
        assertThat(e).isNotNull();
    }

    @Test
    void noAssertionAtAll() {
        String s = "assertEquals(1, 2); { }";
        d.apply(10);
    }

    @Test @Tag("FR-003") @Tag("positive")
    void statusOnly() throws Exception {
        var resp = client.post("/orders");
        assertEquals(201, resp.statusCode());
    }

    @Disabled("flaky")
    @Test @Tag("FR-003") @Tag("positive")
    void skipped() { assertEquals(1, 1); }

    @Test @Tag("US1-AS2") @Tag("positive")
    void usesHelper() throws InterruptedException {
        Thread.sleep(100);
        checkTotal(99.99);
    }

    @Test @Tag("FR-099") @Tag("positive")
    void customLib() {
        ApiAssert.body(resp).hasField("x");
        if (x) { y(); }
    }

    private void checkTotal(double t) {
        assertEquals(t, d.apply(t), 0.001);
    }

    @Nested
    @Tag("FR-002")
    class Inner {
        @Test @Tag("error")
        void nestedTest() {
            try { d.apply(-5); } catch (Exception e) {}
            assertTrue(true);
        }
    }
}
