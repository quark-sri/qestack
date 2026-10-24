# Unit testing recipe: Java

Common stack: JUnit 5 (Jupiter), AssertJ, Mockito. Use what the project already has.

## Run a subset

- Maven: `mvn -q test -Dtest=DiscountTest` or `-Dtest=DiscountTest#appliesTenPercentAt100`
- Gradle: `./gradlew test --tests 'com.acme.DiscountTest'`
- By tag: `@Tag("fast")` on the test, then Maven `-Dgroups=fast` or Gradle `test { useJUnitPlatform { includeTags 'fast' } }`

## Boundary set

```java
@ParameterizedTest(name = "total {0} -> {1}")
@CsvSource({
    "99.99, 99.99",    // just below the limit: no discount
    "100.00, 90.00",   // at the limit: 10% off
    "100.01, 90.01"    // just above
})
void appliesDiscountFromOneHundred(BigDecimal total, BigDecimal expected) {
    assertThat(discount.apply(total)).isEqualByComparingTo(expected);
}
```

## Errors: check the type AND the code or message

```java
assertThatThrownBy(() -> discount.apply(new BigDecimal("-0.01")))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessage("ORD-400");
```

## Time and randomness

- Inject `java.time.Clock`. In the test: `Clock.fixed(Instant.parse("2026-02-28T23:30:00Z"), ZoneOffset.UTC)`.
- Inject `java.util.random.RandomGenerator` or a seeded `new Random(42)`.

## Test doubles

- Mockito for boundaries: `when(rates.current()).thenReturn(new BigDecimal("0.20"));`
- Verify an interaction only when the interaction IS the behavior (a message sent, a payment requested), and check its arguments with `ArgumentCaptor`, not `any()`.

## Pitfalls

- `assertEquals(0.1 + 0.2, 0.3)` fails for `double`. Use `BigDecimal` with `isEqualByComparingTo`, or a tolerance with `isCloseTo(..., within(...))`.
- `@BeforeAll` static state shared between tests creates order dependence.
- `LocalDate.now()` in tests depends on the machine time zone.
