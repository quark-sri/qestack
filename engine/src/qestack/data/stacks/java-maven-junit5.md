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
- Name container-based test classes `*IT` (for example `OrderRepositoryIT`). Failsafe runs only these names by default. Surefire runs `*Test`.
- Never use `@Disabled` in feature tests. The skip gate fails.

## 2. Assertion helpers

The lint gate recognizes these assertion entry points:

- `assert*(...)`, `assertThat(...)`, `fail(...)`, `verify*(...)`, `expect*(...)`, `then(...)`
- Awaitility `untilAsserted(...)`, MockMvc `andExpect(...)`, JSONAssert, StepVerifier

Name your own assertion helpers `assert...`, `verify...` or `expect...`. Then the lint gate sees them. If your internal library uses other names, add them to `.qestack/project.toml` under `extra_custom_assertion_regexes`.

## 3. pom.xml setup

### 3.1 Feature filter for Surefire and Failsafe

The gate tool runs only the tests of one feature. It passes `-Dqe.groups=feature-003`. Configure both plugins to read this property. The gate tool also passes `-Dmaven.test.failure.ignore=true` and `-fae`. Then the Failsafe tests run also when unit tests fail (in the red phase all tests fail), and the gate tool reads the XML reports, not the exit code.

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

The gate tool passes the JUnit random orderers as system properties. Surefire 3.6.0 forwards them to the test JVM (verified: each seed gives another order). If an older Surefire version does not, add this:

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

The gate tool gives each run a new random seed with `{seed}` (`-Djunit.jupiter.execution.order.random.seed={seed}`) and writes the seeds to `flaky.json`. To replay a flaky order, run the command again with the same seed.

It also passes `-Dsurefire.rerunFailingTestsCount=0`. A rerun hides a flaky test. If a report still contains `flakyFailure` or `rerunFailure`, the gate counts the test as flaky.

Time zone and locale cause many flaky Java tests. For high-risk work, run the flaky gate with 10 runs, and add a run with another `user.timezone` and `user.language` (for example through `<argLine>@{argLine} ${qe.jvm.args}</argLine>` and `-Dqe.jvm.args="-Duser.timezone=Asia/Kolkata -Duser.language=de"`).

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
- The gate tool passes `-DtargetClasses=` with only the classes that the feature changed, and `-DtargetTests=` with the test classes of the feature (`{feature_test_classes}`). Without `targetTests`, PIT uses the `targetClasses` pattern as the test filter and misses tests in other packages.
- It passes `-DexcludedGroups=integration,ui`. If your PIT version uses another property name, override `commands.mutation` in `.qestack/project.toml`.
- It passes `-DfailWhenNoMutations=false`. In a multi-module build, a module with no changed classes then does not fail the build.
- Multi-module build: see section 3.4.
- First run the command by hand once. Check that `target/pit-reports/mutations.xml` exists.

### 3.4 Multi-module build

The commands run from the root of the build, with no change. Verified in `examples/order-service-multimodule` (a domain module without tests, and a service module that holds the tests of both).

- **Reports:** the gate tool reads the reports of every module. Surefire and Failsafe write one report folder for each module, and the glob `**/target/surefire-reports/TEST-*.xml` finds them all.
- **Mutation in the module with the tests:** PIT mutates only the classes of the module where it runs. Set `<crossModule>true</crossModule>` in that module, so that PIT also mutates the classes of the modules it depends on. Without it, the classes of the other modules get no mutants, and the score looks better than it is (in the example: 71% instead of 47%).
- **Where to set it:** set `crossModule` in the pom of the module that holds the tests, not on the command line. With `-DcrossModule=true` for all modules, the module without tests also wrote a report (8 mutants, none covered) with the same classes. Set `<skip>true</skip>` for `pitest-maven` in a module without tests, as a second safeguard.
- **Check:** after `qestack mutation`, read the `NOTE no mutants for ... changed file(s)` line, or `changed_without_mutants` in `mutation.json`. Interfaces and records can have no mutants. A class with logic in this list means that PIT did not mutate its module.
- **One module only:** to run the tests of one module, override `commands.test_feature` in `.qestack/project.toml` with `-pl <module> -am`.

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
        return Money.ZERO;   // neutral value: the assertions must fail, not the stub
    }
}
```

- Only public signatures from `plan.md` or `contracts/`. No logic.
- Prefer a neutral return value (`null`, `0`, `BigDecimal.ZERO`, an empty list). Then each test fails on its assertion, and "red" proves that the assertion catches the missing behavior.
- If the neutral value is the expected value of a test (for example "no discount" is 0), that test passes before the implementation. Then throw `UnsupportedOperationException("not implemented: FR-007")` in that method instead.
- `red.json` counts tests that fail with an error (such as the exception of a stub) as `red_by_error`. Set `[gates] red_counts_errors = false` to require assertion failures only.
- List each stub file in `.qestack/runs/<feature>/stubs.json` (a JSON array of paths).

## 6. Check the commands once by hand

These command properties are verified with Maven 3.10.0, Surefire and Failsafe 3.6.0, PIT 1.30.1, JUnit 5.14.4 and Java 25, in `examples/order-service-maven`. Maven ignores an unknown `-D` property without a warning, so the check used the parameter list of each plugin, not only a green build. Older plugin versions can use other names: run each command once in your project, and override `[commands]` in `.qestack/project.toml` if needed.

| Property | Plugin | Check |
|---|---|---|
| `-Dmaven.test.failure.ignore=true` | Surefire, Failsafe | Failsafe tests run when a unit test fails |
| `-Dsurefire.rerunFailingTestsCount=0`, `-Dfailsafe.rerunFailingTestsCount=0` | Surefire, Failsafe (each has its own name) | No reruns |
| `-DfailIfNoTests=false`, `-Dsurefire.failIfNoSpecifiedTests=false` | Surefire | A module without feature tests does not fail |
| `-Djunit.jupiter.*.order.default`, `-Djunit.jupiter.execution.order.random.seed` | Surefire to JUnit | Test order changes between runs (else use section 3.2) |
| `-DtargetTests`, `-DexcludedGroups`, `-DfailWhenNoMutations`, `-DoutputFormats`, `-DtimestampedReports` | pitest-maven | `target/pit-reports/mutations.xml` exists and has only the feature tests in `killingTests` |
