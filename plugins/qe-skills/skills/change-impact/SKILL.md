---
name: change-impact
description: Analyze the impact of a code change (a diff, branch, commit range or pull request) for testing. Finds what the change can break (callers, data, contracts, configuration, other services), which existing tests to run, which tests are missing, and which manual or exploratory checks to do before the merge. Use when the user asks "what should I test for this change?", "what can this PR break?", or needs a focused regression scope.
argument-hint: "[branch, commit range or pull request]"
---

# change-impact

Running all tests is slow, and running none is risky. This skill finds the tests that matter for one change, and the tests that are missing for it.

## Input

The change is `$ARGUMENTS`: a branch, a commit range, a pull request or the uncommitted changes. If it is empty, use the difference between the current branch and the main branch, and say so.

## Steps

1. **Read the change.** List each changed file and what changed: logic, signature, data model, schema or migration, configuration, dependency version, contract, UI, tests only.
2. **Find the reach** of each change:
   - callers and users of the changed functions, classes and endpoints (search the code)
   - data: tables, fields, messages and files that the change reads or writes; old data that a migration must handle
   - contracts: API responses, message formats, public libraries; the consumers of these contracts
   - configuration and feature flags
   - shared code that many areas use
3. **Classify the risk** of each change: high (money, security, data, contracts, shared code, migrations), medium, low (comments, logs, internal names).
4. **Select existing tests.** Find the tests that cover the changed code and its reach (by name, by import, by the code that they call). Order them: fast unit tests for the changed code first, then integration and contract tests for the reach, then the end-to-end journeys that pass through it.
5. **Find missing tests.** For each high or medium change without a strong test: the case to add, with an input and an expected result. Check also that tests changed in the change still check the same behavior or more (a weakened test is a risk).
6. **Manual and exploratory checks.** List the checks that automation does not cover: UI look and feel, a migration on a copy of real data, compatibility with older clients.

## Output

```
## Change impact: <change>

| Changed item | Type | Risk | Reach |
|---|---|---|---|

### Run these existing tests
1. <test or suite> - why

### Add these tests
1. <case>: <input> -> <expected result> (level)

### Weakened or removed tests in this change
- ...

### Manual checks before merge
- ...
```

## Rules

- Search for the real callers. Do not guess the reach from names only.
- A changed test that checks less than before is a finding, also when the build is green.
- Say when the reach is uncertain (dynamic calls, reflection, configuration by name).
