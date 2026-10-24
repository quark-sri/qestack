# Test Quality Guardrails

qestack guardrails, version 1.0. These rules apply to ALL agents in all phases. The hook and the CI guard enforce the most important ones. The rest are instructions that the judge checks.

## G1. Source of truth

1. The specification (`spec.md`, `contracts/`, `data-model.md`) is the source of truth for expected behavior.
2. The implementation is never the source of truth for a test oracle.
3. If the spec is unclear, write an open question. Do not guess. Do not test a `[NEEDS CLARIFICATION]` item as if it were clear.

## G2. Roles

| Role | May read | May write | Must not |
|---|---|---|---|
| Test designer | spec, plan, contracts, data model, rulesets | `test-plan.md` | read the implementation; write code |
| Test writer | test plan, spec, contracts, data model, public signatures, test utilities, rulesets, feedback file | test code, stubs (test-write phase only), `stubs.json`, `suspected-bugs.md`, `suspected-test-defects.md` | read the implementation body of the feature; change production code; read the fault catalog or `seed.json` |
| Code writer | spec, plan, tasks, tests | production code | change, weaken, skip or delete tests |
| Fault seeder | spec, plan, implementation | fault patches and `catalog.json` (with `qestack fault`) | change tests; leave a fault in the code; tell other agents about the faults |
| Judge | everything except the fault patches (it reads `seed-feedback.json`) | `judge.json`, `plan-review.json`, `fault-review.json` | change any code or test |

## G3. Never weaken tests

These actions are never allowed to get a green build:

- delete a test or a test file,
- remove or weaken an assertion,
- add `@Disabled`, `Skip =`, `[Ignore]`, an early `return`, or a try/catch that hides a failure,
- remove a requirement tag or a category tag,
- change an expected value so that it matches the current output of the code,
- widen a tolerance or a timeout without a spec reason.

The hook blocks the first four for locked tests. The guard gate detects them against the base branch.

## G4. When a test fails

1. Compare the test with the spec.
2. If the test is right and the code is wrong → write the case in `runs/<feature>/suspected-bugs.md` (test, requirement, expected, actual, evidence). Do not change the test. This is a good result.
3. If the test is wrong according to the spec → write the case in `runs/<feature>/suspected-test-defects.md`. For a locked test, a human decides.
4. If you cannot decide → ask the user.

## G5. Protected files

Agents must not change: `.qestack/project.toml`, `.qestack/project-rules.md`, local stacks, rulesets and rubrics in `.qestack/`, locks, the equivalent-mutant list, the red-exemption list, `.claude/settings.json`, the installed qestack engine and its bundled files, and the speckit phase commands. Only humans change them, through code review.

## G6. Honest reporting

- Report gate results exactly as the tool prints them.
- Do not say "all tests pass" or "quality is good" without the scorecard.
- If a gate did not run, say so. Do not mark it as passed.
- If you stop early (max iterations, no improvement), say why and list the open items.

## G7. Hidden faults stay hidden

The fault patches and `seed.json` contain the fault details. Only the seeder and humans read them. The writer and the judge use `seed-feedback.json`, which has only the requirement ID and the layer.

## G8. Limits of automation

- Hooks can be bypassed with unusual shell commands. Do not try. The CI guard checks the result against the base branch.
- The lint gate uses patterns. If it reports a false finding, explain it in the summary. Do not change the test to trick the pattern.
