# Stack: .NET (C#)

All agents read this file when `[project] stack` in `.qestack/project.toml` is `dotnet`.

## 1. Tag convention (mandatory)

Use one trait name, `Category`, for all tags. Then one filter works for all of them.

```csharp
[Trait("Category", "feature-003")]
public class OrderDiscountApiTests
{
    [Fact(DisplayName = "TC-014: no discount when the total equals 99.99")]
    [Trait("Category", "FR-007")]
    [Trait("Category", "US1-AS2")]
    [Trait("Category", "boundary")]
    public async Task NoDiscountJustBelowThreshold() { ... }
}
```

- NUnit: `[Category("FR-007")]`. MSTest: `[TestCategory("FR-007")]`. The tool reads all three.
- Never use `Skip =` or `[Ignore]` in feature tests.
- Tag container-based tests `integration` and UI tests `ui`.

## 2. Test results

Install the JUnit XML logger in each test project:

```
dotnet add <TestProject> package JunitXml.TestLogger
```

The stack command writes results to `TestResults/junit/<assembly>.xml`.

## 3. Stryker.NET

```
dotnet tool install --global dotnet-stryker
```

- The stack runs `dotnet stryker --since:<base>` so that only changed code is mutated.
- Run it from the folder where Stryker can find the solution or the test project. If needed, add a `stryker-config.json` and override `commands.mutation` in `.qestack/project.toml`.
- Exclude slow container tests with a test case filter in the Stryker config, if your version supports it.
- Check the report path once by hand. Set `reports.mutation_path` if it differs.

## 4. Assertion helpers

The lint gate recognizes `Assert.*`, FluentAssertions `.Should()`, Shouldly `.ShouldBe*`, Moq `.Verify*`, NSubstitute `.Received*`, Playwright `Expect(...)` and your own helpers named `Assert*`, `Verify*` or `Expect*`. Add other helper names to `extra_custom_assertion_regexes` in `.qestack/project.toml`.

## 5. .NET-specific test rules

- Use `decimal` for money. Compare exact values.
- Use a fake `TimeProvider` (or an `IClock`) for time logic. Do not use `DateTime.Now` in tests.
- Use `WebApplicationFactory<T>` for API tests, with Testcontainers for real dependencies.
- After `Assert.Throws` / `.Should().Throw<T>()`, also check the error code or message.
- Stubs for the red check: `throw new NotImplementedException("FR-007");` and list each stub in `stubs.json`.
