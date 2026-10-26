---
name: qestack
description: "Explains the qestack gated workflow that proves AI-written tests catch bugs, and routes to the right qe-* skill. Use when the user names qestack or a qe-* skill, or asks which qestack step comes next in a repository with .qestack/."
---

# qestack

qestack proves that AI-written tests catch bugs. It does not trust "all green" or coverage. It uses evidence: traceability to requirements, red-before-green, test locks, mutation score, hidden faults and an independent judge.

This skill and the `qe-*` skills are the gated workflow. They need the qestack engine. The other skills of the plugin are the QA library. They need no engine. For QA work outside the gated workflow, use `qa-navigator`.

## Preflight (every qestack skill)

1. Run `qestack --version`. If the command is not found, tell the user to install the engine and stop:
   `pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"`
2. The engine version must have the same major and minor number as this plugin (0.1.x). If not, tell the user to install the matching engine and stop.
3. Check that `.qestack/project.toml` exists. If not, use the `qe-setup` skill first.
4. Find the feature: the folder name under `specs/`, for example `003-order-discount`. If the user did not give it and the branch name does not show it, ask the user. Pass it as `--feature` to every `qestack` command and to every agent.

## How to start a qestack agent

Use the Agent tool. The plugin agents have the prefix `qestack:`, for example `subagent_type: qestack:qe-test-writer`. Put these lines at the start of the prompt. Leave out the lines that do not apply.

```
Feature: <feature folder name>
Mode: <mode of the agent>
Phase: prove | harden          (qe-test-writer in improve mode only)
Iteration: <n>                 (qe-test-judge in test-review mode only)
Feedback: <path>               (qe-test-writer in improve mode only)
```

## Run the long commands in the background

`qestack gate`, `qestack flaky`, `qestack mutation` and `qestack seed` can run longer than the time limit of one shell command. Run them with `run_in_background: true` and wait for the completion notice. Do not poll. If a run stops early, run it again: the engine reverts a fault that a stopped `seed` run left in the code.

## Choose the skill

| The user wants to | Skill | When |
|---|---|---|
| Set up qestack in a repository | `qe-setup` | Once per repository, or when the stack changes |
| Check that a spec is testable | `qe-grill-spec` | Before test design |
| Design tests from a spec | `qe-plan` | Before code exists |
| Write tests from the plan | `qe-write` | After `qe-plan`, before implementation |
| Prove the tests fail first, then lock them | `qe-prove` | After `qe-write`, before implementation |
| Improve the tests until they meet the bar | `qe-harden` | After implementation |
| Get an independent verdict on one feature | `qe-judge` | Any time |
| Measure an existing test suite | `qe-audit` | Any time, read-only |
| Check the judge against human verdicts | `qe-calibrate` | Each sprint |

With the plugin, the full skill names have the prefix `qestack:`, for example `/qestack:qe-plan`.

## Standard flow for a new feature

```
qe-grill-spec -> qe-plan -> qe-write -> qe-prove -> (implement the feature) -> qe-harden
```

With speckit: `qestack init --speckit` adds `/speckit.testplan`, `/speckit.testwrite` and `/speckit.testquality`. They run the same skills.

## Rules for all qestack work

- Read the guardrails: `qestack show guardrails`.
- Report numbers from the engine. Do not give opinions without evidence.
- Never weaken a test to pass a gate. Never change thresholds or protected files.
- Do not edit qestack result files (gate JSON files, `feedback-<n>.md`, `quality-report.md`, `faults/`). Run the command again. The hook blocks these edits.
- A correct test that fails shows a product bug. Report it as a finding.
