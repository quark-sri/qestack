# Ruleset: Playwright UI testing (Java and .NET)

All agents read this file when `ui-playwright` is in `[project] rulesets` of `.qestack/project.toml`. The examples use Java. For .NET, the same rules apply with the .NET API names (`Expect(locator).ToHaveTextAsync(...)`, `WaitForTimeoutAsync`).

## 1. Position in the test strategy

- Test business rules at the API layer. API tests are faster and more stable.
- Use UI tests for user journeys, UI-only behavior (validation messages, navigation, accessibility) and a small number of end-to-end smoke paths.
- Each UI test still traces to a requirement ID and has a category tag.
- Tag UI test classes with `@Tag("ui")`. PIT excludes them. Seeded faults and the judge measure them.

## 2. Assertions

- Use web-first assertions. They retry until the timeout:
  `assertThat(page.getByRole(AriaRole.ALERT)).hasText("Total must be positive")`
- Check a business outcome, not only that an element is visible. "Visible" alone is SHALLOW.
- After a UI action that changes data, check the result in the UI AND, where the test plan says so, through the API or the database.

## 3. Locators

- Prefer `getByRole`, `getByLabel`, `getByText` and `getByTestId`.
- Do not use long CSS or XPath chains. Do not use `nth()` unless the order is a requirement.

## 4. Waits

- Never use `page.waitForTimeout(...)` or `Thread.sleep(...)`. The lint gate reports them as `fixed_sleep`.
- Wait for a state: `assertThat(locator).isVisible()` before the next step is acceptable as a wait, not as the final assertion.

## 5. Isolation and diagnostics

- Use a new browser context for each test.
- Create test data through the API, not through the UI, unless the UI flow is under test.
- Turn on tracing on failure (`context.tracing()`), and keep the trace as a build artifact.

## 6. Seeded faults for this layer (for the fault seeder)

- Validation message not shown for an invalid input
- Wrong value shown (formatting or rounding)
- Button enabled when it must be disabled
- Navigation to the wrong page after submit
- Missing role check: a page or action available to the wrong role
