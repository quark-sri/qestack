# Mutation testing recipe: Java

Common choice: PIT (pitest) with the JUnit 5 plugin, through Maven (`pitest-maven`) or Gradle (`info.solidsoft.pitest`). Use what the project already has.

## Maven, for one class and its tests

```
mvn -q test-compile org.pitest:pitest-maven:mutationCoverage \
  -DtargetClasses='com.acme.order.Discount*' \
  -DtargetTests='com.acme.order.DiscountTest*' \
  -DoutputFormats=XML,HTML -DtimestampedReports=false
```

The plugin needs the `pitest-junit5-plugin` dependency for JUnit 5 tests. Reports go to `target/pit-reports/` (`mutations.xml`, `index.html`).

## Gradle

Configure the `pitest` block (`targetClasses`, `targetTests`, `junit5PluginVersion`, `outputFormats`), then run `./gradlew pitest`. Reports go to `build/reports/pitest/`.

## Reading the report

- `SURVIVED`: a test ran the line and did not notice the change. A missing or weak assertion.
- `NO_COVERAGE`: no test ran the line.
- `KILLED`, `TIMED_OUT`: detected.

## Tips

- Exclude slow container tests from mutation runs (for example by tag or by name), and measure them with hand-made faults instead.
- Use the incremental history option for repeated runs on large modules.
