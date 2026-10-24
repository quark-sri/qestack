---
name: qestack
description: Entry point for qestack AI test quality. Use when the user asks about qestack, asks how to make AI-written tests trustworthy, asks which qestack step to run next, or asks "are these tests good enough?". Explains the workflow and routes to the right qe-* skill.
---

# qestack

qestack proves that AI-written tests catch bugs. It does not trust "all green" or coverage. It uses evidence: traceability to requirements, red-before-green, test locks, mutation score, hidden faults and an independent judge.

## Preflight (every qestack skill)

1. Run `qestack --version`. If the command is not found, tell the user to install the engine and stop:
   `pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"`
2. Check that `.qestack/project.toml` exists. If not, use the `qe-setup` skill first.

## Choose the skill

| The user wants to | Skill | When |
|---|---|---|
| Set up qestack in a repository | `qe-setup` | Once per repository, or when the stack changes |
| Check that a spec is testable | `qe-grill-spec` | Before test design |
| Design tests from a spec | `qe-plan` | Before code exists |
| Write tests from the plan | `qe-write` | After `qe-plan`, before implementation |
| Prove the tests fail first, then lock them | `qe-prove` | After `qe-write`, before implementation |
| Improve the tests until they meet the bar | `qe-harden` | After implementation |
| Get an independent verdict only | `qe-judge` | Any time |
| Measure an existing test suite | `qe-audit` | Any time, read-only |
| Check the judge against human verdicts | `qe-calibrate` | Each sprint |

## Standard flow for a new feature

```
qe-grill-spec -> qe-plan -> qe-write -> qe-prove -> (implement the feature) -> qe-harden
```

With speckit: `qestack init --speckit` adds `/speckit.testplan`, `/speckit.testwrite` and `/speckit.testquality`. They run the same skills.

## Rules for all qestack work

- Read the guardrails: `qestack show guardrails`.
- Report numbers from the engine. Do not give opinions without evidence.
- Never weaken a test to pass a gate. Never change thresholds or protected files.
- A correct test that fails shows a product bug. Report it as a finding.
