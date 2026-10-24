# Benchmarks (planned for 0.3)

The benchmark answers one question: **do tests built with qestack find more real bugs than tests from a plain prompt?**

## Method

1. Take 30 to 50 real bugs from [Defects4J](https://github.com/rjust/defects4j). Each bug has a buggy version, a fixed version and a bug report.
2. For each bug, write a short requirement (`spec.md`) from the bug report and the fixed behavior. Do not mention the bug.
3. **Arm A:** an agent writes tests with a plain prompt ("write thorough tests for this requirement").
4. **Arm B:** the same agent and model with qestack (`qe-plan`, `qe-write`, `qe-harden`).
5. Run both test sets against the fixed version (all must pass) and against the buggy version.
6. Measure for each arm:
   - bugs detected (a test fails on the buggy version)
   - mutation score on the changed classes
   - hollow, trivial and shallow test rate
   - agent tokens, cost and time
7. Repeat each arm 3 times to measure the variance.

## Rules

- Publish the method, the requirement texts, the raw results and the scripts.
- Publish negative results too.
- Freeze the model version and the qestack version for each run.
