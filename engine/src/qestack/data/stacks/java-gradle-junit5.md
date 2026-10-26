# Stack: Java + Gradle + JUnit 5

All agents read this file when `[project] stack` in `.qestack/project.toml` is `java-gradle-junit5`.

This stack reads Java tests in the same way as `java-maven-junit5`. Sections 1, 2 and 4 to 6 are the same as in that guide. Only the build setup (section 3) and the commands differ. The examples use the Kotlin DSL. For the Groovy DSL, write the same settings in `build.gradle`.

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
- Put container-based tests in the `integrationTest` suite (`src/integrationTest/java`, see section 3.1). Name the classes `*IT`.
- Never use `@Disabled` in feature tests. The skip gate fails.

## 2. Assertion helpers

The same as in `java-maven-junit5`: `assert*(...)`, `assertThat(...)`, `fail(...)`, `verify*(...)`, `expect*(...)`, `then(...)`, Awaitility, MockMvc, JSONAssert and StepVerifier. Name your own helpers `assert...`, `verify...` or `expect...`. Add other names to `extra_custom_assertion_regexes` in `.qestack/project.toml`.

## 3. build.gradle.kts setup

The commands use the Gradle wrapper (`./gradlew`). Commit the wrapper, so that every run uses the Gradle version of the project.

### 3.1 Test suites, feature filter and failures

The gate tool runs only the tests of one feature. It passes `-Pqe.groups=feature-003`. Configure every `Test` task to read this property. It also runs both the `test` and the `integrationTest` tasks, with `--continue`.

```kotlin
testing {
    suites {
        getByName<JvmTestSuite>("test") {
            useJUnitJupiter("5.14.4")
        }
        // Container-based tests (*IT)
        register<JvmTestSuite>("integrationTest") {
            useJUnitJupiter("5.14.4")
            dependencies { implementation(project()) }
            targets.all { testTask.configure { shouldRunAfter("test") } }
        }
    }
}

// Empty or missing means: run all tests. The gate tool sets it with -Pqe.groups=feature-NNN
val qeGroups = providers.gradleProperty("qe.groups").orElse("")

tasks.withType<Test>().configureEach {
    useJUnitPlatform {
        if (qeGroups.get().isNotBlank()) includeTags(qeGroups.get())
    }
    // In the red phase every test fails. The gate tool reads the XML reports, not the exit code.
    ignoreFailures = true
    // Gradle does not pass -D from the command line to the test JVM: forward the -Pjunit.* settings.
    providers.gradlePropertiesPrefixedBy("junit.").get().forEach { (key, value) -> systemProperty(key, value) }
    // Without this, Gradle skips the task when nothing changed, and no new XML report is written.
    outputs.upToDateWhen { false }
}
```

If the project has no integration tests, the `integrationTest` suite can stay empty: Gradle then runs no tests and writes no report. Gradle reports are in `build/test-results/test/` and `build/test-results/integrationTest/`.

### 3.2 Random order for the flakiness gate

The gate tool passes the JUnit random orderers as `-Pjunit.*` properties. The forwarding code in section 3.1 sends them to the test JVM (verified: each seed gives another order).

The gate tool gives each run a new random seed with `{seed}` (`-Pjunit.jupiter.execution.order.random.seed={seed}`) and writes the seeds to `flaky.json`. To replay a flaky order, run the command again with the same seed.

Gradle has no test rerun by default. If you use the `org.gradle.test-retry` plugin, set `retry { maxRetries = 0 }` for the gate runs. A rerun hides a flaky test. If a report still contains `flakyFailure` or `rerunFailure`, the gate counts the test as flaky.

Time zone and locale cause many flaky Java tests. For high-risk work, run the flaky gate with 10 runs, and add a run with another `user.timezone` and `user.language` (for example `jvmArgs(providers.gradleProperty("qe.jvm.args").map { it.split(" ") }.getOrElse(emptyList()))` and `-Pqe.jvm.args="-Duser.timezone=Asia/Kolkata -Duser.language=de"`).

### 3.3 PIT (mutation testing)

Use the `info.solidsoft.pitest` plugin. Do not make a lifecycle task depend on `pitest`. The gate tool calls it directly, with `--rerun`: without it, Gradle skips the task when nothing changed, and the gate finds no new report.

```kotlin
plugins {
    java
    id("info.solidsoft.pitest") version "1.19.0"   // set the current release
}

pitest {
    pitestVersion = "1.30.1"                        // set the current release
    junit5PluginVersion = "1.2.3"                   // set the current release
    mutators = setOf("STRONGER")
    outputFormats = setOf("XML", "HTML")
    timestampedReports = false
    threads = 4
    timeoutConstInMillis = 8000
    failWhenNoMutations = false
    excludedGroups = setOf("integration", "ui")
    // The gate tool sets these for each run (class patterns, separated by commas).
    providers.gradleProperty("qe.targetClasses").orNull?.let { targetClasses = it.split(",").toSet() }
    providers.gradleProperty("qe.targetTests").orNull?.let { targetTests = it.split(",").toSet() }
}
```

Notes:

- The gate tool passes `-Pqe.targetClasses=` with only the classes that the feature changed, and `-Pqe.targetTests=` with the test classes of the feature (`{feature_test_classes}`). Without `targetTests`, PIT uses the `targetClasses` pattern as the test filter and misses tests in other packages.
- `failWhenNoMutations = false`: in a multi-module build, a module with no changed classes does not fail the build.
- Multi-module build: the gate tool reads every `mutations.xml` that the run wrote (one for each module). You can also run PIT only in the module that holds the changed classes: override `commands.mutation` with `:module:pitest`.
- First run the command by hand once. Check that `build/reports/pitest/mutations.xml` exists.

## 4. Java-specific test rules

The same as in `java-maven-junit5`:

- Use JUnit 5 assertions or AssertJ. Do not use `System.out` to show results.
- Compare decimal money values with `BigDecimal.compareTo` or AssertJ `isEqualByComparingTo`.
- Use `@ParameterizedTest` for boundary sets. Each row has its own expected value from the spec.
- Use a fixed `Clock` for time logic.
- Use `assertThrows` and then check the exception type AND the error code or message.
- For Spring Boot: prefer slice tests (`@WebMvcTest`, `@DataJpaTest`). Use `@SpringBootTest` with Testcontainers for integration tests.

## 5. Stubs for the red check

The same as in `java-maven-junit5`. Prefer a neutral return value in a stub. If the neutral value is the expected value of a test, throw `UnsupportedOperationException("not implemented: FR-007")`. List each stub file in `.qestack/runs/<feature>/stubs.json`.

## 6. Check the commands once by hand

These commands are verified with Gradle 9.8.2, the PIT plugin 1.19.0, PIT 1.30.1, JUnit 5.14.4 and Java 25, in `examples/order-service-gradle`. The example gives the same mutation result as the Maven example (47%, 7 of 15 mutants killed). Run each command once in your project, and override `[commands]` in `.qestack/project.toml` if needed.

| Check | How |
|---|---|
| The feature filter runs only the tests of one tag | `./gradlew test -Pqe.groups=feature-001`, then look at `build/test-results/test/` |
| A red test does not stop the build | The exit code is 0 and the XML report holds the `<failure>` |
| Random order changes between seeds | Run with seeds 1, 2 and 3 and compare the order of the `testcase` entries |
| The `integrationTest` suite runs and writes a report | Add one `*IT` test and check `build/test-results/integrationTest/` |
| PIT writes `build/reports/pitest/mutations.xml` | Only the feature tests are in `killingTests` |
