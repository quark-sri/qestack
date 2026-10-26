---
description: "Session test S2: a request to review a few tests starts testcase-reviewer, not the panel."
tags: [routing]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review these tests. Are they any good?

```java
@Tag("feature-001")
class DiscountTest {
    private final Discount d = new Discount();

    @Test
    void discountAtThreshold() {
        assertEquals(90.0, d.apply(100.0), 0.001);
    }

    @Test
    void hollowTest() {
        // TODO write this
    }

    @Test
    void negativeTotalOnlyNotNull() {
        var e = assertThrows(IllegalArgumentException.class, () -> d.apply(-1));
        assertThat(e).isNotNull();
    }

    @Disabled("flaky")
    @Test
    void skipped() { assertEquals(1, 1); }
}
```
