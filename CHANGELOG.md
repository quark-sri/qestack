# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project uses [semantic versioning](https://semver.org/).

## [0.1.0] - unreleased

### Added

- Engine `qestack` (Python 3.11+, no dependencies): `init`, `doctor`, `context`, `show`, `lint`, `trace`, `snapshot`, `red`, `lock`, `flaky`, `mutation`, `fault`, `seed`, `guard`, `gate`, `score`, `feedback`, `calibrate`, `hook`.
- Stacks: `java-maven-junit5` (PIT), `dotnet` (Stryker.NET).
- Rulesets: `api-http`, `database`, `kafka`, `ui-playwright`.
- Rubrics: test review (R1–R7), plan review (P1–P7), fault catalog.
- Claude Code plugin: 10 skills, 4 agents, guard hook, marketplace manifest.
- Speckit adapter: `/speckit.testplan`, `/speckit.testwrite`, `/speckit.testquality`.
- Documentation, project plan, CI workflow, static example.
- Plugin `qe-skills`: 35 Quality Engineering skills for any project, with no engine, in 10 categories. Tool-neutral `SKILL.md` files, stack recipes for Java, TypeScript and Python in `references/`, and a shared `.agents/qa-project-context.md`.
- `qe-skills` reviewer personas: 8 persona files in `test-review-panel/references/personas/` (AI Behavior Auditor, Hallucination Checker, Domain Oracle Reviewer, Saboteur, Test Automation Architect, Determinism and Flakiness Engineer, Maintainability Craftsperson, Suite Cost and Speed Reviewer). Only the `test-review-panel` skill uses them. It starts one agent for each persona and merges the findings. The `test-reviewer` agent (no edit tool) runs the read-only personas. The `test-saboteur` agent runs the personas that change code. The other skills do not depend on them.
- `scripts/validate_repo.py` checks every plugin, the reference files of each skill, duplicate skill names and the marketplace sources. For `qe-skills`, it also checks the routing parts of each description, the related skills, the required sections, the shared context and that `SKILL.md` names no tools.

### Changed (architecture review)

- Held-out faults: a share of the seeded faults (`loop.holdout_ratio`) never appears in the feedback. The seed gate uses them.
- `quality-report.md` has no fault details. The details are in `<runs_dir>/faults/undetected.md` (not committed). The judge writes `faults/fault-review.json`.
- New gates `trivial` and `shallow`. Only strong (OK) tests count for requirement coverage. Tests skipped at run time fail the `skipped` gate.
- `red.json` reports `red_by_error`. New setting `gates.red_counts_errors`.
- Flaky gate: a seed for each random-order run, and Surefire rerun passes count as flaky.
- Mutation: `{feature_test_classes}` placeholder, one report for each module.
- `seed` and `fault` are safe after a stopped run. `fault begin --force`. `fault save --layer` accepts `domain|api|db|kafka|ui`. Faults can add new files.
- Hook: blocks agent edits of engine result files and shell writes to locked tests. It warns when the engine is missing. `QESTACK_HOOK_LOG` logs the hook input.
- `context` lists `changed_source_files` and uses project copies of rubrics and templates.
- Placeholders are shell-quoted. Commands that change files need an exact feature.
- TQS: requirement depth uses the depth ratio only. Judge: R3 < 3 gives revise; evidence needs a file and line or a spec anchor.
- Skills and agents: `qestack:` agent handoffs with fixed inputs, writer phases, judge audit-sample mode, neutral stubs.
- Rulesets: more database, Kafka and API rules and required cases.
