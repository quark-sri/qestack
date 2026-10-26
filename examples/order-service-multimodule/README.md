# Example: order service (runnable, multi-module Maven)

The same code and tests as `examples/order-service-maven`, split into two Maven modules:

- `order-domain`: `Discount`, `OrderException`, `OrderDiscounted`, `EventPublisher`. It has no tests of its own.
- `order-service`: `OrderService` and `WeakDiscountTest`. The tests cover the classes of both modules.

This shows the multi-module settings of the stack `java-maven-junit5` (section 3.4 of its guide). The commands are the stack defaults. No command is overridden.

## Run it

You need Java 17 or later, Maven 3.9 or later and the `qestack` engine. From this folder:

```bash
qestack doctor
qestack lint --feature 001
qestack trace --feature 001
qestack flaky --feature 001 --runs 3
qestack mutation --feature 001
```

## Results

Measured on 2026-10-26 with Maven 3.10.0, Surefire 3.6.0, PIT 1.30.1, JUnit 5.14.4 and Java 25.

| Gate | Result |
|---|---|
| flaky | 4 tests x 2 runs, 0 flaky |
| mutation, with `crossModule` | score 47% (7 of 15 killed), the same as the single-module example. The survivors in `order-domain` are listed with their module path. |
| mutation, without `crossModule` | score 71% (5 of 7 killed). PIT mutates only `OrderService`. The 8 mutants of `order-domain` are missing. |
| mutation, `-DcrossModule=true` on the command line | The module without tests also writes a report (8 mutants, none covered) for the same classes. Set `crossModule` in the pom of the test module instead. |

## The settings that matter

- `order-service/pom.xml`: `crossModule` for `pitest-maven`.
- `order-domain/pom.xml`: `skip` for `pitest-maven`. This module has no tests. It is a safeguard.
- `pom.xml` (parent): the `qe.groups` property and the plugin settings, shared by both modules.
