# qestack handoff: current state and next tasks

| | |
|---|---|
| For | Claude (desktop app / Claude Code) on the owner's MacBook |
| Owner | quark-sri (GitHub). A personal repository of the owner. |
| Updated | 2026-10-26 |
| State | Release 0.1 in progress. All work is on `main` and pushed. CI is green. |
| Repository | `github.com/quark-sri/qestack`, **public** (owner decision) |
| Scope of release 0.1 | AI test quality for **Java with Maven and JUnit 5**. .NET is experimental. |
| Writing standard | Simplified Technical English (STE). See `docs/writing-style.md`. |

Read this whole file before you start. Then read `docs/PLAN.md`, `docs/architecture.md` and `CONTRIBUTING.md`.

---

## 1. What qestack is

qestack is an open-source toolbox of **skills, plugins and agents for AI Quality Engineering**. Its first capability, and the scope of release 0.1, is **AI test quality**: proof that AI-written tests catch bugs.

It has three parts:

1. **Engine:** the `qestack` command (Python 3.11+, standard library only) in `engine/`. It runs the gates: lint, traceability, red-before-green, flakiness, mutation score, hidden (seeded) faults, guard, locks, score, feedback and judge calibration.
2. **Plugin `qestack`:** `plugins/qestack/`. One plugin with two groups (2026-10-26):
   - **Gated workflow:** the skills `qestack` and `qe-*` (10), the 4 `qe-*` workflow agents and the guard hook. They need the engine.
   - **QA library:** 39 Quality Engineering skills for any project and any stack, 8 review personas, and the `test-review-panel` skill. They need no engine.
3. **Project folder in user repositories:** `.qestack/` (settings, gate results, locks) for the engine, and `.agents/qa-project-context.md` (project facts) for the library.

The owner is a test automation architect. The first target users are Java teams with Maven, JUnit 5, HTTP API tests (an internal library on top of `HttpClient`), database tests and Kafka tests. Playwright UI tests come later.

## 2. Decisions already made

Do not change these without the owner's approval. "2026-10-24" marks the decisions that the owner made in the session of that date.

### Project

| Topic | Decision |
|---|---|
| Name and position | `qestack`: "QA and test automation skills, agents and quality gates for AI coding agents" (2026-10-26; before: "skills, plugins and agents for AI Quality Engineering"). Release 0.1 is "AI test quality", the first capability. The name stays `qestack` for discovery; "QA skills" goes in descriptions and keywords. (2026-10-24, 2026-10-26) |
| Repository | Public. It is the owner's personal repository, and the owner decided to make it public. (2026-10-24) |
| Publishing | Do not publish to PyPI. Do not create tags or releases without the owner. |
| License | Apache-2.0 |
| Problem tracking | No GitHub issues. Track problems as tasks in `TASKS.local.md` (git-ignored through `.git/info/exclude`, never pushed). (2026-10-24) |
| Acknowledgement | The README credits `petrkindlmann/qa-skills` (MIT) as the inspiration for the QA library structure. Keep it. (2026-10-24) |
| One plugin | `qe-skills` is merged into the `qestack` plugin. The name `qe-skills` is dropped. The engine stays optional: library skills work without it, gated skills stop in the preflight. Final merge decisions D1 to D11 are in the pull request of branch `merge-qe-skills-into-qestack`. (2026-10-26) |

### Engine and the `qestack` plugin

| Topic | Decision |
|---|---|
| Engine language | Python 3.11+, no dependencies |
| Config names | **stack** (exactly one), **ruleset** (zero or more), **project settings** (`.qestack/project.toml`), **project rules** (`.qestack/project-rules.md`). Do not use the old word "overlay". |
| Agent names | `qe-test-designer`, `qe-test-writer`, `qe-test-judge`, `qe-fault-seeder` |
| Skill names | `qestack`, `qe-setup`, `qe-grill-spec`, `qe-plan`, `qe-write`, `qe-prove`, `qe-harden`, `qe-judge`, `qe-audit`, `qe-calibrate` |
| Speckit | Optional adapter only (`qestack init --speckit`). qestack must work without speckit. |
| Scope of 0.1 | Java + Maven + JUnit 5. `.NET` files stay in the repository, marked "experimental". Do not spend time on .NET. |
| Examples | No Spring Boot. Plain Java, so that the examples build fast. (2026-10-24) |

### The QA library in the `qestack` plugin (2026-10-24, merged 2026-10-26)

| Topic | Decision |
|---|---|
| Groups by name | `qestack` and `qe-*` skills are the gated workflow. All other skills are the library. `qe-*` agents are workflow agents. All other agents are personas. The validator uses these names. (2026-10-26) |
| Skills | A QA discipline library, 39 skills in 10 categories. Each `SKILL.md` gives the method and names no tools. Tool details are in `references/` stack recipes (Java, TypeScript and JavaScript, Python). |
| Shared context | `qa-project-context` writes `.agents/qa-project-context.md`. Every other skill reads it first. |
| Personas | 8 agents in `plugins/qestack/agents/`: `ai-behavior-auditor`, `hallucination-checker`, `domain-oracle-reviewer`, `saboteur`, `test-automation-architect`, `determinism-flakiness-engineer`, `maintainability-craftsperson`, `suite-cost-speed-reviewer`. |
| Personas only report | No persona has an edit tool or changes a file. The caller (a skill or the main agent) makes every change. The Saboteur designs a fault plan; the caller runs it in an isolated copy with the `mutation-probe` method. |
| Persona commands | Personas may run only read-only commands and the test command of the brief. One shared "Reviewer rules" section, the same in all 8 personas. |
| Who uses personas | Only `test-review-panel`, also after the merge. No gated skill uses them until the session tests pass, so that persona output cannot leak held-out faults. Users can start a persona directly, or from their own skills. (2026-10-24, kept 2026-10-26) |
| Review results | The panel lead writes `qa-reviews/<date>-<scope>/` (`panel-report.md`, `findings.json`, `personas/`). Reviewers write no files. |

### Style

All docs, skills, agent prompts and CLI messages in STE. `scripts/validate_repo.py` warns about sentences longer than 30 words in skills and agents.

## 3. Current state

### Done and checked

- Engine with 19 commands. The tests pass: `python3 -m unittest discover -s engine/tests` (end-to-end tests in `test_cli.py`, in-process rule tests in `test_rules.py`).
- CI is green on ubuntu and macOS, Python 3.11 to 3.13. The CI builds and installs the package, so the package data (`qestack/data/**`) is in the wheel.
- Plugin `qestack`: 10 gated skills, 4 workflow agents, hook. Architecture review fixes are in (held-out faults, the `trivial` and `shallow` gates, fault recovery, a stricter hook and others; see `CHANGELOG.md`).
- QA library in the `qestack` plugin: 39 skills, 8 personas, `test-review-panel` with the findings format. Merged from the old `qe-skills` plugin (2026-10-26).
- `scripts/validate_repo.py`: 0 errors, 0 warnings. It checks the plugin, the library rules (routing parts, related skills, no tool names, shared context) and the persona rules (sections, the same shared rules, no edit tools, only the panel uses them).
- Stack `java-gradle-junit5` and `examples/order-service-gradle` (PR #1).
- Task 3: `examples/order-service-maven` runs every gate with real Maven. All Java stack command properties are checked against the plugin parameter lists (Surefire and Failsafe 3.6.0, PIT 1.30.1). Random order, the Failsafe feature filter and PIT on Java 25 work.
- Local tools on the MacBook: Java 25 (Temurin) and Maven 3.10.0 through SDKMAN, Python 3.14. The engine runs from a virtual environment (`pip install -e ./engine`).

### Not verified yet

| Item | Risk | Task |
|---|---|---|
| The plugins in a real Claude Code session | Skill discovery, agent start, the hook and the review panel are not tested. | 4a, 4b |
| Stack recipe code in the library | The recipe samples (Pact, k6, Gatling, axe and others) were not run. | later |

## 4. Local setup on the MacBook

The setup is done. To repeat it on a new machine:

1. **Python 3.11 or later:** `python3 --version`.
2. **Engine:**
   ```bash
   python3 -m venv .venv && .venv/bin/pip install -e ./engine
   .venv/bin/qestack --version && .venv/bin/qestack show
   ```
   If `qestack show` fails with "Nothing found" or a missing file, the package data is not installed. Fix `engine/pyproject.toml` (`[tool.setuptools.package-data]`).
3. **Java and Maven** with SDKMAN: `sdk install java 21-tem` (or use the installed 25), `sdk install maven`. Then `java -version` and `mvn -version`.
4. **Check:**
   ```bash
   python3 -m unittest discover -s engine/tests -v
   python3 scripts/validate_repo.py
   ```

## 5. Tasks, in this order

Use a task list. Commit after each task. End each commit message with the trailer lines that your Claude Code environment requires. Record problems in `TASKS.local.md`, not as GitHub issues.

| Task | State |
|---|---|
| 1. Push to GitHub | Done. Public, by owner decision. |
| 2. Make CI green | Done. |
| 4a. Test the QA library in a real session | Ready. The owner runs the slash commands. |
| 3. Runnable Maven example | Done, except step 3b (the strengthened tests come from `/qe-harden` in task 4b). |
| 4b. Test the `qestack` plugin in a real session | After task 3. |
| 5. Integration example with database and Kafka | After 4b. |
| 6. Multi-module Maven | Done (PR #2): `examples/order-service-multimodule` and section 3.4 of the Java Maven stack guide. Merged before task 5. |
| 7. Release preparation | Last. Do not publish. |

Finished tasks, for reference only (do not redo them):

- Task 3: `examples/order-service-maven` runs every gate with real Maven. The results are in its README. Step 3b (the strengthened tests) comes from `/qe-harden` in task 4b.
- Task 6: `examples/order-service-multimodule` and section 3.4 of `java-maven-junit5.md` (PR #2).

### Task 4a: Test the QA library in a real Claude Code session

Follow `docs/library-session-test.md`. The routing checks S2, S3, S4 and S7 now run as plugin evals (`plugins/qestack/evals/routing/`, results of 2026-10-26 in that document: 23 of 24 runs, then 4 of 5 for the flaky case). The other checks stay manual. It has 22 checks (skills, personas, review panel) and an answer key of 14 expected findings for `examples/order-discount`.

1. The owner installs the plugin and runs the slash commands. Claude cannot type `/plugin` or `/agents`.
2. Record each result and problem in `TASKS.local.md`.
3. Fix the skills and personas. Then decide if the personas need a hook that blocks file writes (checks P4 and R8).

**Done when:** all 22 checks pass, and the panel finds at least 11 of the 14 expected findings.

### Task 4b: Test the `qestack` plugin in a real Claude Code session

1. Install from the local folder:
   ```
   /plugin marketplace add /Users/srinivas/Documents/repos/qestack
   /plugin install qestack@qestack
   ```
2. In `examples/order-service-maven`, run the full flow: `/qe-setup`, `/qe-grill-spec`, `/qe-plan`, `/qe-write`, `/qe-prove`, implement, `/qe-harden`.
3. Check:
   - each skill starts and calls the right engine commands
   - each agent starts (designer, writer, judge, fault seeder)
   - the hook blocks a weakening edit on a locked test, and allows a strengthening edit
   - the hook blocks a forged engine result file, and a shell write to a locked test
   - the writer does not read the implementation (check the transcript)
   - the writer never sees the fault details, and the holdout faults are not in the feedback
4. Record every problem in `TASKS.local.md`, then fix the skills and agents.

**Done when:** one feature goes from spec to an ACCEPT report with the plugin, and the hook works.

### Task 5: Integration example with database and Kafka

1. Add a second feature to the Maven example (or a second example) with Testcontainers: PostgreSQL and Kafka. No Spring Boot.
2. Tag the integration tests `integration`.
3. Check that PIT skips them, and that the seeded faults measure them (`database` and `kafka` rulesets: "Seeded faults for this layer").
4. Show how to register an internal HTTP client library in `project.toml` (`extra_custom_assertion_regexes` and `extra_shallow_statement_regexes`). Use a small fake library in the example.

**Done when:** the hidden faults for the database and Kafka layers are detected, and the report shows it.

### Task 7: Release preparation (do not publish)

1. Update `CHANGELOG.md`.
2. Run `python3 scripts/validate_repo.py` and the tests.
3. Check that the versions are equal in the engine, both plugins and the marketplace.
4. Ask the owner to review. Do not publish to PyPI. Do not create a tag or a release without the owner.

## 6. Rules for this work

1. Write all text in STE (`docs/writing-style.md`).
2. Keep the engine free of dependencies.
3. Each engine change needs a test in `engine/tests/test_cli.py`.
4. Run the tests and the validator before each commit.
5. Keep the versions equal in `engine/src/qestack/__init__.py`, `plugins/qestack/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (the validator checks this).
6. Do not change .NET files, except to keep the tests green.
7. Do not add the owner's employer code, names or data to the repository.
8. Do not publish packages. Do not create tags or releases without the owner. The repository is public: treat each commit as public.
9. Do not commit `qestack-0.1.0.bundle`, `qestack-0.1.0.zip` or `TASKS.local.md`.
10. QA library: no tool names in `SKILL.md`; personas never change files; only `test-review-panel` uses the personas.
11. Ask the owner before you change a decision in section 2.

## 7. File map

| Path | Content |
|---|---|
| `engine/src/qestack/cli.py` | All engine commands (one file) |
| `engine/src/qestack/data/defaults.toml` | Core defaults: paths, gates, weights, loop |
| `engine/src/qestack/data/stacks/java-maven-junit5.{toml,md}` | The Java stack (verified in task 3) |
| `engine/src/qestack/data/rulesets/*.md` | API, database, Kafka, UI rules for agents |
| `engine/src/qestack/data/rubrics/*.md` | Judge rubrics |
| `engine/src/qestack/data/templates/` | Files that `qestack init` and `qestack show` use |
| `engine/src/qestack/data/adapters/speckit/` | Speckit commands and constitution text |
| `engine/tests/test_cli.py` | End-to-end tests (fake test runner, no Maven) |
| `plugins/qestack/skills/{qestack,qe-*}/SKILL.md` | The 10 gated workflow skills |
| `plugins/qestack/agents/qe-*.md` | The 4 workflow agents |
| `plugins/qestack/hooks/hooks.json` | The guard hook |
| `plugins/qestack/skills/*/SKILL.md` (other names) | The 39 library skills, with `references/` |
| `plugins/qestack/agents/*.md` (other names) | The 8 review personas |
| `plugins/qestack/skills/test-review-panel/references/findings-format.md` | The findings block and the review folder format |
| `.claude-plugin/marketplace.json` | Marketplace entry for the plugin |
| `scripts/validate_repo.py` | Repository checks |
| `scripts/install-skills.sh` | Installs the skills for other agents (`--agent <name>`), from the portable packages |
| `scripts/build_skills.py` | Builds the portable skill packages in `dist/` |
| `docs/PLAN.md` | Vision, roadmap, governance, risks |
| `docs/library-session-test.md` | The checks for task 4a |
| `TASKS.local.md` | Local problem and task list (not in git) |

## 8. Known issues

| Issue | Note |
|---|---|
| Lint is pattern based | False findings are possible. Registered helpers reduce them. |
| The hook fails open | On an internal error, the hook allows the action and prints a warning. CI is the authority. |
| Windows | Not supported in 0.1. The test fixtures use POSIX commands. |
| `qestack red` after the implementation | Not possible. Tests added in the harden loop are measured by mutation and seeded faults instead. |
| Speckit FR numbers restart in each feature | Handled by the feature tag (`feature-NNN`). |
| Personas can run commands | A shell command can write files. The shared rules forbid it, and the panel checks the working tree. A blocking hook is a task 4a decision. |
| The `qe-fault-seeder` agent changes production code | By design of the gated workflow, through the engine (`fault begin`, `fault save`). The "personas only report" rule is for the review personas only. |

## 9. Open questions for the owner

None. Earlier questions and their answers (2026-10-24):

1. Employer open-source policy: not relevant. qestack is the owner's personal repository.
2. When to make the repository public: it is public, by owner decision.
3. Spring Boot in the example: no Spring Boot.
