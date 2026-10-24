---
name: qe-prove
description: Prove that the new feature tests fail before the implementation exists (red-before-green), then lock them so that later work cannot weaken them. Use after qe-write and before the implementation.
---

# qe-prove

A test that passes before the feature exists does not test the feature. This skill proves "red", then locks the tests.

## Steps

1. **Preflight.** `qestack --version` works and `.qestack/project.toml` exists.
2. **Red check.** Run `qestack red --feature <feature>`.
   - Status `INVALID`: the tests do not compile, or the command is wrong. Fix the build (stubs or test code), then run again.
   - A test passes before the implementation: launch `qe-test-writer` in improve mode with this reason: "This test passes before the feature exists. It does not test the new behavior." If the behavior really existed before (brownfield), ask the user. Only the user may add the test key to `.qestack/locks/<feature>.red-exempt.json`.
   - Repeat until every test fails, or for at most 3 rounds.
3. **Lock.** Run `qestack lock --feature <feature> --phase prove`.
4. **Report** to the user: red tests and total, exemptions requested, the lock file path.
5. **Next step:** implement the feature (for example `/speckit.implement`). The implementation must make these tests pass without changing them. Then run `qe-harden`.

## Rules

- Red must come from the missing behavior. Never add tricks such as `fail()` at the start of a test.
- Commit `<runs_dir>/red.json` and the lock file. CI uses them later.
