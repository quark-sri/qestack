---
name: change-impact
description: "Analyzes what a diff, branch or pull request can break, which existing tests to run in which order, which tests are missing and which changed tests now check less. Use when the user says 'regression scope' or asks 'what should I test for this change' or 'what can this PR break'. Not for running the tests (use test-runner)."
license: Apache-2.0
argument-hint: "[branch, commit range or pull request]"
---

# change-impact

## Objective

Running all tests is slow, and running none is risky. This skill finds the tests that matter for one change, the tests that are missing for it, and the tests that the change weakened.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its test commands, levels and risk areas.
2. If it does not exist, read the build files and the test layout. Do not stop the work for the context file.

## Discovery questions

1. Which change? If none is given, use the difference between the current branch and the main branch, and say so.
2. Is there a ticket or a description of the intent?

## Workflow

1. **Read the change.** For each changed file: logic, signature, data model, schema or migration, configuration, dependency version, contract, UI, or tests only.
2. **Find the reach** of each change:
   - the callers of changed functions, classes and endpoints (search the code)
   - the data that the change reads or writes, and old data that a migration must handle
   - the consumers of changed contracts
   - configuration, feature flags and shared code
3. **Classify the risk** of each change: high (money, security, data, contracts, shared code, migrations), medium, low.
4. **Select existing tests** that cover the changed code and its reach. Order them: fast tests of the changed code, then integration and contract tests of the reach, then the end-to-end journeys through it.
5. **Missing tests:** for each high or medium change without a strong test, the case to add with an input and an expected result.
6. **Weakened tests:** compare each changed test with its old version. Removed assertions, removed cases, added skips, looser expected values or tolerances are findings.
7. **Manual checks:** what automation does not cover (look and feel, a migration on a copy of real data, older clients).

## Output

```
## Change impact: <change>

| Changed item | Type | Risk | Reach |
|---|---|---|---|

Run these tests: ...
Add these tests: <case>: <input> -> <expected> (level)
Weakened or removed tests: ...
Manual checks before merge: ...
```

## Anti-patterns

- **Reach guessed from names.** Search for the real callers.
- **A green build as proof.** A weakened test is green too.
- **Ignoring configuration and migrations.** They break production without a code error.

## Done when

- Each changed item has a type, a risk and its reach.
- The tests to run are listed in order; the missing and the weakened tests are listed.
- Uncertain reach (dynamic calls, reflection, configuration by name) is stated.

## Related skills

- `test-runner`: run the selected tests.
- `risk-based-testing`: the risk scale.
- `test-planning`: for a release with many changes.
- `testcase-reviewer`: review the changed tests.
