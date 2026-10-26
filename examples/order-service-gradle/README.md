# Example: order service (runnable, Gradle)

The same project as `examples/order-service-maven`, built with Gradle (Kotlin DSL), JUnit 5 and the PIT Gradle plugin. It uses the stack `java-gradle-junit5`. The sources, the spec and the weak tests are the same, so the results can be compared.

`build.gradle.kts` holds the settings that qestack needs: the `-Pqe.groups` tag filter, `-Pjunit.*` forwarding for random order, `ignoreFailures` and the `pitest` block. See `qestack show stacks/java-gradle-junit5`.

## Run it

You need Java 17 or later (the build compiles for 17 with the JDK that runs Gradle) and the `qestack` engine. The Gradle wrapper is in the folder. From this folder:

```bash
qestack doctor
qestack lint --feature 001
qestack trace --feature 001
qestack flaky --feature 001 --runs 3
qestack mutation --feature 001
qestack score --feature 001
```

## Results

Measured on 2026-10-26 with Gradle 9.8.2, the PIT plugin 1.19.0, PIT 1.30.1, JUnit 5.14.4 and Java 25.

| Gate | Result |
|---|---|
| doctor | stack, commands and report globs found; 5 test methods parsed |
| flaky | 4 tests x 3 random-order runs, 0 flaky; four seeds gave four different orders |
| mutation | score 47% (7 of 15 killed), the same as the Maven example |

The `red`, `seed` and `score` gates need the stub, fault and judge steps (see the Maven example). They do not depend on the build tool.
