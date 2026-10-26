---
name: qe-audit
description: "Reports the quality of an existing test suite or module with qestack, read-only and also without feature tags: weak and skipped tests, traceability, mutation score and a judge sample. Use when the user asks how good a whole suite is, or wants a baseline before adopting qestack."
---

# qe-audit

This skill changes no code and no tests.

## Steps

1. **Preflight.** `qestack --version` works. If `.qestack/project.toml` does not exist, ask the user before you run `qestack init`. It creates `.qestack/` in the repository.
2. **Doctor.** Run `qestack doctor`. Note the problems. Continue if lint can run.
3. **Static scan.** Run `qestack lint --all --json --max 100`. Summarize: total tests, hollow, no assertion, trivial, shallow, skipped, TODO, untraced, smells by type. List the 10 worst files.
4. **Traceability.** If a spec folder exists and tests carry tags, run `qestack trace --feature <feature>` for each feature that the user names.
5. **Mutation (optional).** Tell the user that mutation testing can take a long time. If the user agrees, run `qestack mutation --feature <feature> --all-files` in the background, or the mutation command for a module that the user names. Report the score and the files with the most surviving mutants.
6. **Judge sample (optional).** If the user agrees, choose about 20 tests: the worst lint findings and some random tests. Start `qestack:qe-test-judge` (Mode: audit-sample) with the list of exact test keys from step 3.
7. **Report.** Write `.qestack/audit-<date>.md`:
   - summary numbers
   - top risks (for example "42% of API tests check only the status code")
   - the 10 worst files
   - surviving mutant hot spots
   - judge findings
   - a plan: what to fix first, and which qestack skills to adopt
   Then give the user a short summary.

## Rules

- Report numbers, not impressions. Say which checks did not run and why.
- Pattern-based lint can give false findings. Mark findings that you checked by hand.
