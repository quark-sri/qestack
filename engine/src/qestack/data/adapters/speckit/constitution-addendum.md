# Constitution addendum: qestack test quality

> Add this section to `.specify/memory/constitution.md` (or run `/speckit.constitution` and
> give it this text). The numbers come from `.qestack/project.toml`.

### Principle: Tests Prove Requirements, Not Code (NON-NEGOTIABLE)

1. **Spec-first tests.** Tests are designed from `spec.md`, contracts and the data model, in `test-plan.md`, before the implementation. The agent that writes tests does not read the implementation of the feature.
2. **Traceability.** Every functional requirement (`FR-###`), acceptance scenario (`US#-AS#`) and edge case (`EC-##`) has at least one test. Each test carries the feature tag, its requirement IDs and a category tag.
3. **Red before green.** Each new test fails before the feature is implemented. A test that passes before the implementation does not count.
4. **Locked tests.** After `/speckit.testwrite`, the feature tests are locked. The implementation phase must not delete, skip or weaken them, or remove their tags. Adding tests and strengthening assertions is allowed.
5. **Fault detection.** A feature is done only when the quality gates pass: mutation score on changed code ≥ the project threshold, seeded-fault detection ≥ the project threshold, no hollow, assertion-free, skipped or flaky tests, and Test Quality Score ≥ the project minimum.
6. **Independent review.** A separate judge agent reviews all feature tests against the rubric. No test may have a "reject" verdict.
7. **Bugs are findings.** When a correct test fails, the code is fixed. The test is never changed to match wrong behavior.
8. **Protected quality configuration.** Thresholds, rubrics, rulesets, the gate tool and locks change only through human review.

### Workflow additions

- After `/speckit.plan`: run `/speckit.testplan`.
- After `/speckit.tasks`: run `/speckit.testwrite`. Test tasks in `tasks.md` refer to `TC-###` IDs from `test-plan.md`; `/speckit.implement` does not re-create these tests.
- After `/speckit.implement`: run `/speckit.testquality`. The feature is complete only when it reports ACCEPT, or a human signs off an ESCALATE report.
