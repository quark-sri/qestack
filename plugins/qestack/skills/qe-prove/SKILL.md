---
name: qe-prove
description: qestack red-before-green. Proves that the new feature tests fail before the implementation exists, then locks them so that later work cannot weaken them. Use in a qestack repository after qe-write and before the implementation.
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-prove

A test that passes before the feature exists does not test the feature. This skill proves "red", then locks the tests.

## Steps

1. **Preflight.** Do the preflight of the `qestack` skill. The feature is `$ARGUMENTS`. If it is empty, find it as the preflight says.
2. **Red check.** Run `qestack red --feature <feature>`. Read every line of the output:
   - Status `INVALID`: the tests do not compile, or the command is wrong. Start `qestack:qe-test-writer` (Feature, Mode: write) with the compile errors. If the command is wrong, tell the user which `[commands]` entry to fix and stop.
   - `PASSES BEFORE IMPLEMENTATION: <key>`: start `qestack:qe-test-writer` (Feature, Mode: improve, Phase: prove) with these test keys and this reason: "This test passes before the feature exists. It does not test the new behavior." If the behavior really existed before (brownfield), ask the user. Only the user may add the test key to `.qestack/locks/<feature>.red-exempt.json`.
   - `NOT RUN: <key>`: the build did not run this test. Check the `test_feature` command and the feature tag of the test class. Tell the user. Do not lock.
   - `FAILS ONLY WITH AN ERROR: <key>`: the test fails only because a stub throws (`red_counts_errors = false`). Start the writer (Feature, Mode: improve, Phase: prove) with this reason: "Change the stub to return a neutral value (stack guide, section 5)."
   - A NOTE about `red_by_error`: report the number to the user. Many errors and few assertion failures make the red evidence weak.
3. **Repeat** step 2 until the command exits with 0, for at most 3 rounds. If it still fails after 3 rounds, stop. Do not lock. Report the test keys and the reason for each.
4. **Lock.** Run `qestack lock --feature <feature> --phase prove`.
5. **Report** to the user: red tests and total (by assertion, by error), exemptions requested, the lock file path.
6. **Next step:** implement the feature (for example `/speckit.implement`). The implementation must make these tests pass without changing them. Then run `qe-harden`.

## Rules

- Red must come from the missing behavior. Never add tricks such as `fail()` at the start of a test.
- Commit `<runs_dir>/red.json` and the lock file. CI uses them later.
