# Pipeline recipes

Use the commands of the project. These are common forms.

## Test reports (JUnit XML is read by most pipeline platforms)

| Stack | Report |
|---|---|
| Java, Maven | Surefire writes `target/surefire-reports/TEST-*.xml`; Failsafe writes `target/failsafe-reports/TEST-*.xml` |
| Java, Gradle | `build/test-results/test/TEST-*.xml` |
| TypeScript, Vitest | `vitest run --reporter=junit --outputFile=reports/junit.xml` |
| TypeScript, Jest | `jest-junit` reporter |
| TypeScript, Playwright | `reporter: [['junit', { outputFile: 'reports/junit.xml' }], ['html']]` |
| Python, pytest | `pytest --junitxml=reports/junit.xml` |

## Sharding and parallel runs

| Stack | Option |
|---|---|
| Java, Maven | `-T 1C` for modules; Surefire `forkCount` and JUnit parallel execution for tests |
| Java, Gradle | `maxParallelForks`; split test classes across jobs by a list |
| Playwright | `npx playwright test --shard=1/4` |
| Vitest | `vitest run --shard=1/4` |
| Jest | `jest --shard=1/4` |
| pytest | `pytest -n auto` (pytest-xdist) inside a job; split files across jobs by a list |

## Stage order (typical)

1. Build, static checks, dependency scan
2. Unit tests (+ coverage)
3. API and integration tests with containers
4. Contract tests and provider verification
5. End-to-end smoke for the critical journeys
6. Deploy to a test environment, then post-deploy smoke
7. Nightly: full end-to-end, performance, security scans, mutation testing on critical modules

## Caching

Cache the dependency folder (for example the Maven or Gradle cache, the package manager cache, the Python wheel cache), keyed by the lock file hash.

## Blocking

The test command's exit code must fail the job. Do not add `|| true` or "continue on error" to a gate. Upload reports in a step that runs also on failure.
