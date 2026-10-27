# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project uses [semantic versioning](https://semver.org/).

## [0.1.0] - unreleased

### Added

- Engine `qestack` (Python 3.11+, no dependencies): `init`, `doctor`, `context`, `show`, `lint`, `trace`, `snapshot`, `red`, `lock`, `flaky`, `mutation`, `fault`, `seed`, `guard`, `gate`, `score`, `feedback`, `calibrate`, `hook`.
- Stacks: `java-maven-junit5` (PIT), `java-gradle-junit5` (PIT), `dotnet` (Stryker.NET).
- Rulesets: `api-http`, `database`, `kafka`, `ui-playwright`.
- Rubrics: test review (R1–R7), plan review (P1–P7), fault catalog.
- Claude Code plugin `qestack`: 49 skills (10 gated skills that use the engine, 39 library skills that do not), 12 agents (4 workflow agents, 8 reviewer personas), guard hook, marketplace manifest.
- Speckit adapter: `/speckit.testplan`, `/speckit.testwrite`, `/speckit.testquality`.
- Documentation, project plan, CI workflow, static example.
- Library skills: 39 Quality Engineering skills for any project, with no engine, in 10 categories. Tool-neutral `SKILL.md` files, stack recipes for Java, TypeScript and Python in `references/`, and a shared `.agents/qa-project-context.md`.
- Reviewer personas: 8 agents in `plugins/qestack/agents/` (AI Behavior Auditor, Hallucination Checker, Domain Oracle Reviewer, Saboteur, Test Automation Architect, Determinism and Flakiness Engineer, Maintainability Craftsperson, Suite Cost and Speed Reviewer). In this plugin, only the `test-review-panel` skill uses them. No persona has an edit tool: personas find and report, and the caller changes code. The Saboteur returns a fault plan; the panel runs it with the `mutation-probe` method in an isolated copy. All personas share one "Reviewer rules" section: no fixes, file:line evidence, and a findings block in one format. Users can start a persona directly. The panel starts several, in parallel, and merges the findings. The panel saves each run in `qa-reviews/<date>-<scope>/` (`panel-report.md`, `findings.json`, `personas/`). The other skills do not depend on them.
- `scripts/validate_repo.py` checks every plugin, the reference files of each skill, duplicate skill names and the marketplace sources. For the library skills, it also checks the routing parts of each description, the related skills, the required sections, the shared context and that `SKILL.md` names no tools.

- Library gaps closed after a review of related projects: new skills `testability-review`, `production-testing`, `resilience-testing` and `localization-testing`; a property-based testing recipe in `unit-testing`; tautology checks and eight named sycophancy patterns in the `ai-behavior-auditor` persona; `qa-navigator` routes to the new skills.
- Faster setup: `scripts/install.sh` (engine and plugins in one step, `--skills-only` for the skills alone). `qestack init` gets `--hook` (merge the guard hook into `.claude/settings.json`), `--existing` (lower start thresholds) and ends with a lint preview and next steps.
- Runnable example `examples/order-service-maven` (plain Java, no Spring Boot). All gates run with real Maven; the README has the results.

- Runnable example `examples/order-service-multimodule` (two Maven modules) and a multi-module section in the Java Maven stack guide: `crossModule` for PIT, `skip` for modules without tests.
- `qestack mutation` lists the changed source files that have no mutants (`changed_without_mutants` in `mutation.json`, and a NOTE line). A module that PIT does not mutate no longer hides behind a good score.
- Stack `java-gradle-junit5` and the runnable example `examples/order-service-gradle` (Gradle 9.8.2, PIT plugin 1.19.0). Same Java reading rules as the Maven stack. The commands run the `test` and `integrationTest` suites, filter by tag with `-Pqe.groups`, forward the JUnit random-order settings with `-Pjunit.*` and run PIT through the Gradle plugin. The example gives the same mutation result as the Maven example (47%, 7 of 15). `qestack init` picks this stack when it finds `build.gradle` or `build.gradle.kts`.

### Fixed

- The engine finds the nearest `.qestack/` from the current folder, and `qestack init` in a sub-project with its own build file creates `.qestack/` there (monorepos). Before, it always used the top of the git repository.
- In a project below the git top, `changed_files` and the base version of a file used paths from the git top. Now they use paths from the project root (`git diff --relative`, `git show <ref>:./<path>`).
- Java stack: `-Dfailsafe.rerunFailingTestsCount=0`. Failsafe has its own property name, so reruns of integration tests were not turned off.
- Java stack commands are verified with Maven 3.10.0, Surefire and Failsafe 3.6.0, PIT 1.30.1, JUnit 5.14.4 and Java 25.

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

### Fixed (review panel, 2026-10-27)

- Hook: it finds the qestack project from the edited file, so a session started at the root of a monorepo guards its sub-projects.
- Hook: it sees the lock of a feature whose name contains a dot. It blocks `qestack lock` with an abbreviated `--force` and `qestack init --force` or `--existing` in an existing project. The CLI no longer accepts abbreviated options.
- Hook: it protects `.qestack/guardrails.md`, `.qestack/templates/`, `.qestack/adapters/` and `.claude/settings.local.json`. A copy of a guidance file in `.qestack/` wins over the bundled file, so agents must not write it.
- A lock file that cannot be read, or that a newer engine wrote, no longer turns the protection off: the hook blocks edits to test files, and `lock` and `guard` stop with an error.
- Result and lock files have a `schema` field (1). The engine refuses a file with a newer schema. Files without the field are schema 1.
- JSON results are written to a temporary file and then renamed, so a stopped run leaves no half-written file. `score --ci` skips an invalid line in `history.jsonl`, as the local `score` does.
- `gate` builds the options of each step with the real parser.
- Skills: `test-environments` no longer uses the 'pass locally, fail in CI' trigger of `flaky-test-detective`. `qe-test-writer` may change the stubs listed in `stubs.json` in improve mode, phase prove, as `qe-prove` asks. New routing eval `no-skill-general` (a general request starts no skill) and a `test-environments` check in `flaky-test`.
- New tests: the hook cases above, `calibrate`, `gate`, the PIT and Stryker parsers, and an in-process rule file (`engine/tests/test_rules.py`).

### Changed (any-agent support, 2026-10-27)

- License: qestack now uses the MIT License (before: Apache License 2.0). The `NOTICE` file is removed. The Gradle wrapper in `examples/order-service-gradle` keeps its own Apache 2.0 license.
- `docs/other-agents.md`: new tables for Claude Code, Codex, Cursor, GitHub Copilot (CLI and VS Code), Gemini CLI, Antigravity, Devin Desktop (was Windsurf), Cline and OpenCode. Each row gives the skill folders, `.agents/skills` support, unknown frontmatter keys, sub-agents and hooks, with a link to the official documentation and the date of the check. The old unverified paths are gone.
- Skills follow the Agent Skills spec: each `SKILL.md` has `license: MIT`, and the 10 gated skills have a `compatibility` line (engine, git, shell; full guard only in Claude Code). The validator checks the spec rules for name, description (1-1024 characters), `compatibility` (at most 500) and `metadata`. The new `--spec <skill-folder>` mode checks a folder against the spec only and rejects the Claude Code fields. New tests in `scripts/tests/`, also in CI.

### Changed (one plugin)

- One plugin: the `qe-skills` plugin is now part of the `qestack` plugin. The 39 library skills and the 8 review personas are in `plugins/qestack/`. The library still needs no engine; only the gated skills (`qestack`, `qe-*`) need it. Skill commands change from `/qe-skills:<skill>` to `/qestack:<skill>`. If you installed the old plugin, run `/plugin uninstall qe-skills@qestack`, then `/plugin install qestack@qestack`.
- The validator finds the skill groups and agent classes by name. `qa-navigator` routes to the gated workflow. `qe-setup` and `qa-project-context` share the project facts. `mutation-probe` and `flaky-test-detective` use the engine commands when the repository has qestack.
- `docs/qe-skills-session-test.md` is now `docs/library-session-test.md`, with a new routing check (S7).
- Skill descriptions follow the Claude standards: third person, the key use case first, "Use when" triggers and, for library skills, "Not for ... (use <skill>)". They are at most 350 characters each and 15,000 in total (before: 32,075). The "Related:" list is only in the body.
- The validator checks the Claude skill and agent standards: name format, known frontmatter keys, description form and size, existing skills in descriptions and "Related skills", body size, reference depth and contents, known agent tools, and no fields that plugin agents ignore. See `docs/guides/adding-a-skill.md`.
