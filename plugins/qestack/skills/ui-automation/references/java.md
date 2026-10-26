# UI automation recipe: Java

Common choices: Playwright for Java, or Selenium WebDriver (often with a wrapper such as Selenide). Use what the project already has.

## Playwright for Java

```java
@Test
@DisplayName("TC-021: a buyer can pay an order and sees the confirmation")
void buyerPaysOrder() {
    String orderNo = api.createOrderFor(buyer);                 // set up through the API
    page.navigate(baseUrl + "/orders/" + orderNo);
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Pay now")).click();
    assertThat(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName("Payment received"))).isVisible();
    assertThat(page.getByTestId("order-status")).hasText("PAID");   // retrying assertion
    org.assertj.core.api.Assertions.assertThat(api.orderStatus(orderNo)).isEqualTo("PAID");
}
```

`assertThat(Locator)` comes from `com.microsoft.playwright.assertions.PlaywrightAssertions` and retries until the timeout.

- Reuse the login: save the storage state once, then create each browser context with `setStorageStatePath(...)`.
- Record a trace for failed tests: start tracing for each context, and save it only when the test fails.

## Selenium WebDriver

- Use explicit waits: `new WebDriverWait(driver, Duration.ofSeconds(10)).until(ExpectedConditions.textToBe(By.cssSelector("[data-testid=order-status]"), "PAID"))`.
- Do not mix implicit and explicit waits.
- Prefer `By.cssSelector("[data-testid=...]")` or accessible attributes over layout-bound XPath.
- Take a screenshot and save the browser log in a JUnit extension when a test fails.
