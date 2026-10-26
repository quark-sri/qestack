# Accessibility testing recipe: Java

Common choice: axe-core through a Java integration for the UI framework (for example the Deque axe integrations for Selenium or Playwright for Java). Use what the project already has.

## Playwright for Java with axe

```java
@Test
void checkoutPageHasNoSeriousViolations() {
    page.navigate(baseUrl + "/checkout");
    AxeResults results = new AxeBuilder(page)
        .withTags(List.of("wcag2a", "wcag2aa", "wcag21a", "wcag21aa"))
        .analyze();
    List<Rule> serious = results.getViolations().stream()
        .filter(v -> List.of("serious", "critical").contains(v.getImpact()))
        .toList();
    assertThat(serious).as(describe(serious)).isEmpty();
}
```

- Run the check again after each important state change (an error shown, a dialog open).
- Check the class and package names for the axe integration version in the project.

## Selenium

The axe Selenium integration has the same shape: build an analyzer for the driver, choose the rule tags, analyze, and fail on serious and critical violations.
