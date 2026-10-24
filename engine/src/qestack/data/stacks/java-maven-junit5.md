# Stack: Java + Maven + JUnit 5

All agents read this file when `[project] stack` in `.qestack/project.toml` is `java-maven-junit5`.

## 1. Tag convention (mandatory)

Each test class has a feature tag. Each test method has at least one requirement ID and at least one category.

```java
@Tag("feature-003")                       // speckit feature number
class OrderDiscountApiTest {

    @Test
    @Tag("FR-007") @Tag("US1-AS2")       // requirement IDs from spec.md / test-plan.md
    @Tag("boundary")                      // category
    @DisplayName("TC-014: no discount when the total equals 99.99")
    void noDiscountJustBelowThreshold() { ... }
}
```

- Categories: `positive`, `negative`, `boundary`, `error`, `security`, `contract`, `performance`, `resilience`, `idempotency`, `concurrency`.
- Put the test case ID (`TC-###` from `test-plan.md`) at the start of `@DisplayName`.
- Tag container-based tests with `@Tag("integration")`. Tag UI tests with `@Tag("ui")`. PIT excludes these tags because they are slow under mutation testing. Seeded faults measure them instead.
- Never use `@Disabled` in feature tests. The skip gate fails.

## 2. Assertion helpers

The lint gate recognizes these assertion entry points:

- `assert*(...)`, `assertThat(...)`, `fail(...)`, `verify*(...)`, `expect*(...)`, `then(...)`
- Awaitility `untilAsserted(...)`, MockMvc `andExpect(...)`, JSONAssert, StepVerifier

Name your own assertion helpers `assert...`, `verify...` or `expect...`. Then the lint gate sees them. If your internal library uses other names, add them to `.qestack/project.toml` under `extra_custom_assertion_regexes`.

## 3. pom.xml setup

### 3.1 Feature filter for Surefire and Failsafe

The gate tool runs only the tests of one feature. It passes `-Dqe.groups=feature-003`. Configure both plugins to read this property:

```xml
<properties>
  <!-- Empty means: run all tests. The gate tool sets it with -Dqe.groups=feature-NNN -->
  <qe.groups></qe.groups>
</properties>

<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-surefire-plugin</artifactId>
  <configuration>
    <groups>${qe.groups}</groups>
  </configuration>
</plugin>

<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-failsafe-plugin</artifactId>
  <configuration>
    <groups>${qe.groups}</groups>
  </configuration>
  <executions>
    <execution>
      <goals><goal>integration-test</goal><goal>verify</goal></goals>
    </execution>
  </executions>
</plugin>
```

### 3.2 Random order for the flakiness gate

The gate tool passes the JUnit random orderers as system properties. If your Surefire version does not forward them to the test JVM, add this:

```xml
<configuration>
  <properties>
    <configurationParameters>
      junit.jupiter.testmethod.order.default=${qe.method.order}
      junit.jupiter.testclass.order.default=${qe.class.order}
    </configurationParameters>
  </properties>
</configuration>
```

Then set `test_feature_random` in `.qestack/project.toml` to pass `-Dqe.method.order=org.junit.jupiter.api.MethodOrderer$Random` and `-Dqe.class.order=org.junit.jupiter.api.ClassOrderer$Random`.

### 3.3 PIT (mutation testing)

```xml
<properties>
  <!-- Set these to the current releases on Maven Central -->
  <pitest.version>SET-CURRENT-VERSION</pitest.version>
  <pitest.junit5.version>SET-CURRENT-VERSION</pitest.junit5.version>
</properties>

<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version>${pitest.version}</version>
  <dependencies>
    <dependency>
      <groupId>org.pitest</groupId>
      <artifactId>pitest-junit5-plugin</artifactId>
      <version>${pitest.junit5.version}</version>
    </dependency>
  </dependencies>
  <configuration>
    <mutators><mutator>STRONGER</mutator></mutators>
    <outputFormats><param>XML</param><param>HTML</param></outputFormats>
    <timestampedReports>false</timestampedReports>
    <threads>4</threads>
    <timeoutConstant>8000</timeoutConstant>
  </configuration>
</plugin>
```

Notes:

- Do not bind PIT to a lifecycle phase. The gate tool calls it directly.
- The gate tool passes `-DtargetClasses=` with only the classes that the feature changed.
- It passes `-DexcludedGroups=integration,ui`. If your PIT version uses another property name, override `commands.mutation` in `.qestack/project.toml`.
- Multi-module build: run PIT in the module that holds the changed classes (`-pl <module>`), or use a PIT aggregation setup.
- First run the command by hand once. Check that `target/pit-reports/mutations.xml` exists.

## 4. Java-specific test rules

- Use JUnit 5 assertions or AssertJ. Do not use `System.out` to show results.
- Compare decimal money values with `BigDecimal.compareTo` or AssertJ `isEqualByComparingTo`. Do not compare `double` values without a tolerance.
- Use `@ParameterizedTest` for boundary sets. Each row must have its own expected value from the spec. Do not compute the expected value with the production formula.
- Use a fixed `Clock` for time logic. Do not call `LocalDate.now()` in tests.
- Use `assertThrows` and then check the exception type AND the error code or message. A type check alone is weak.
- For Spring Boot: prefer slice tests (`@WebMvcTest`, `@DataJpaTest`) for speed. Use `@SpringBootTest` with Testcontainers for integration tests.

## 5. Stubs for the red check

Before implementation, tests must compile and fail. If a production class does not exist yet, the test writer may create a stub:

```java
public class DiscountService {
    public Money apply(Order order) {
        throw new UnsupportedOperationException("not implemented: FR-007");
    }
}
```

- Only public signatures from `plan.md` or `contracts/`. No logic.
- List each stub file in `.qestack/runs/<feature>/stubs.json` (a JSON array of paths).
