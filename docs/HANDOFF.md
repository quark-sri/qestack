# qestack handoff: continue the work on the local machine

| | |
|---|---|
| For | Claude (desktop app / Claude Code) on the owner's MacBook |
| Owner | quark-sri (GitHub) |
| Date | 2026-10-24 |
| State | Release 0.1 in progress. One local commit on `main`. Not pushed. |
| Scope now | **Java with Maven and JUnit 5 only.** .NET is out of scope until release 0.2. |
| Writing standard | Simplified Technical English (STE). See `docs/writing-style.md`. |

Read this whole file before you start. Then read `docs/PLAN.md`, `docs/architecture.md` and `CONTRIBUTING.md`.

---

## 1. What qestack is

qestack is an open-source project. It proves that AI-written tests catch bugs. It has three parts:

1. **Engine:** the `qestack` command (Python 3.11+, standard library only) in `engine/`. It runs the gates: lint, traceability, red-before-green, flakiness, mutation score, hidden (seeded) faults, guard, locks, score, feedback and judge calibration.
2. **Claude Code plugin:** `plugins/qestack/`. It has 10 skills, 4 agents and a guard hook.
3. **Project folder in user repositories:** `.qestack/` (settings, gate results, locks).

The owner is a test automation architect. The first target users are Java teams with Maven, JUnit 5, HTTP API tests (an internal library on top of `HttpClient`), database tests and Kafka tests. Playwright UI tests come later.

## 2. Decisions already made

Do not change these without the owner's approval.

| Topic | Decision |
|---|---|
| Name | `qestack` ("QE stack"). Always describe it as "qestack AI test quality" (the name looks like Qt's `QStack` to search engines). |
| Repository | `github.com/quark-sri/qestack`, **private** until the owner reviews it. |
| License | Apache-2.0 |
| Engine language | Python 3.11+, no dependencies |
| Config names | **stack** (exactly one), **ruleset** (zero or more), **project settings** (`.qestack/project.toml`), **project rules** (`.qestack/project-rules.md`). Do not use the old word "overlay". |
| Agent names | `qe-test-designer`, `qe-test-writer`, `qe-test-judge`, `qe-fault-seeder` |
| Skill names | `qestack`, `qe-setup`, `qe-grill-spec`, `qe-plan`, `qe-write`, `qe-prove`, `qe-harden`, `qe-judge`, `qe-audit`, `qe-calibrate` |
| Speckit | Optional adapter only (`qestack init --speckit`). qestack must work without speckit. |
| Scope of 0.1 | Java + Maven + JUnit 5. `.NET` files stay in the repository, marked "experimental". Do not spend time on .NET. |
| Style | All docs, skills, agent prompts and CLI messages in STE. `scripts/validate_repo.py` warns about sentences longer than 30 words in skills and agents. |

## 3. Current state

### Done and tested (in the cloud workspace)

- Engine with 19 commands. 14 end-to-end tests pass: `python3 -m unittest discover -s engine/tests`.
- Plugin: marketplace manifest, plugin manifest, 10 skills, 4 agents, hook.
- Bundled data: core defaults, stacks (`java-maven-junit5`, `dotnet`), rulesets (`api-http`, `database`, `kafka`, `ui-playwright`), rubrics (test, plan, fault catalog), guardrails, templates, speckit adapter.
- Docs: README, PLAN, getting started, architecture, configuration, why-qestack (metrics), landscape, other agents, CI, writing style, guides for new stacks and rulesets.
- Repository: LICENSE, NOTICE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, GitHub CI workflow, issue and PR templates, `scripts/validate_repo.py` (0 errors, 0 warnings), `scripts/install-skills.sh`, a static example (`examples/order-discount`).

### Not verified yet (the cloud workspace had no access to Maven Central or PyPI)

| Item | Risk |
|---|---|
| `pip install ./engine` and `python -m build engine` | Package data (`qestack/data/**`) may not be in the wheel. |
| The Maven commands in `engine/src/qestack/data/stacks/java-maven-junit5.toml` | Property names can be wrong for the current plugin versions. |
| PIT `-DexcludedGroups=integration,ui` | The PIT Maven property name may differ. |
| Surefire forwards `-Djunit.jupiter...order.default` to the test JVM | Random order may not work; the stack guide has a `configurationParameters` fallback. |
| Failsafe `<groups>${qe.groups}</groups>` | Not tested with a real build. |
| The plugin in a real Claude Code session | Skill discovery, agent launch and the hook from `hooks/hooks.json` are not tested. |
| macOS | The engine tests ran on Linux only. |

## 4. Local setup on the MacBook

1. **Python 3.11 or later.** Run `python3 --version`. If it is older: `brew install python@3.12`.
2. **Get the code.** The owner has `qestack-0.1.0.bundle` (with history) and `qestack-0.1.0.zip`. Prefer the bundle:
   ```bash
   git clone qestack-0.1.0.bundle qestack
   cd qestack
   git remote remove origin
   ```
3. **Check:**
   ```bash
   python3 -m unittest discover -s engine/tests -v
   python3 scripts/validate_repo.py
   ```
4. **Install the engine in editable mode:**
   ```bash
   brew install pipx   # if needed
   pipx install -e ./engine
   qestack --version
   qestack show
   ```
   If `qestack show` fails with "Nothing found" or a missing file, the package data is not installed. Fix `engine/pyproject.toml` (`[tool.setuptools.package-data]`), then check again.
5. **Java tools:** Java 17 or 21 and Maven 3.9+ (`java -version`, `mvn -version`). The owner may use SDKMAN (`~/.sdkman` exists).

## 5. Tasks, in this order

Use a task list. Commit after each task. End each commit message with the trailer lines that your Claude Code environment requires.

### Task 1: Push to GitHub (private)

1. The owner creates the empty private repository `quark-sri/qestack`, or runs:
   ```bash
   gh repo create quark-sri/qestack --private --source . --remote origin
   ```
2. Push `main`, and also push a review branch:
   ```bash
   git push -u origin main
   git switch -c init/v0.1 && git push -u origin init/v0.1
   ```
3. Do not make the repository public. The owner decides that after review.

**Done when:** the repository exists, it is private, and the GitHub CI workflow ran.

### Task 2: Make CI green

1. Open the Actions tab. Fix every failure in `.github/workflows/ci.yml`.
2. The "Build and install the package" step proves that the wheel contains `qestack/data/**`. If it fails, fix the packaging.

**Done when:** all CI jobs pass on ubuntu and macos, Python 3.11 to 3.13.

### Task 3: Runnable Maven example (most important)

Create `examples/order-service-maven/`. It replaces "static only" in the README.

1. A small Maven project (no Spring for now, so that it builds fast):
   - Java 17, JUnit 5 (Jupiter), AssertJ
   - `Discount` and `OrderService` classes with the rules from `examples/order-discount/specs/001-order-discount/spec.md`
   - Surefire and Failsafe with `<groups>${qe.groups}</groups>` and the property `<qe.groups></qe.groups>`
   - PIT (`pitest-maven` + `pitest-junit5-plugin`), current versions from Maven Central, not bound to a phase
2. `.qestack/project.toml` with `stack = "java-maven-junit5"`.
3. Two test classes:
   - `WeakDiscountTest` with tag `feature-001`: typical weak AI tests (status-only, not-null, hollow, skipped)
   - after `/qe-harden`: the strengthened tests
4. Run each engine command by hand and record the results:
   ```bash
   cd examples/order-service-maven
   qestack doctor
   qestack lint --feature 001
   qestack trace --feature 001
   qestack red --feature 001        # on a stub version of the code
   qestack flaky --feature 001 --runs 3
   qestack mutation --feature 001   # needs a change against the base ref
   qestack fault begin --feature 001   # then inject one fault, then:
   qestack fault save --feature 001 --id F01 --req FR-001 --layer domain
   qestack seed --feature 001
   qestack score --feature 001
   ```
5. Fix every wrong command, property name or report path in `engine/src/qestack/data/stacks/java-maven-junit5.toml` and in `java-maven-junit5.md`.
6. Add a short "Results" section to the example README with the real numbers.

**Done when:** every command above works on the MacBook with real Maven, and the stack file has no unverified commands.

### Task 4: Test the plugin in a real Claude Code session

1. Install from the local folder:
   ```
   /plugin marketplace add /path/to/qestack
   /plugin install qestack@qestack
   ```
2. In `examples/order-service-maven`, run the full flow: `/qe-setup`, `/qe-grill-spec`, `/qe-plan`, `/qe-write`, `/qe-prove`, implement, `/qe-harden`.
3. Check:
   - each skill starts and calls the right engine commands
   - each agent starts (designer, writer, judge, fault seeder)
   - the hook blocks a weakening edit on a locked test, and allows a strengthening edit
   - the writer does not read the implementation (check the transcript)
   - the writer never sees the fault details
4. Write every problem as a GitHub issue, then fix the skills and agents.

**Done when:** one feature goes from spec to an ACCEPT report with the plugin, and the hook works.

### Task 5: Integration example with database and Kafka

1. Add a second feature to the Maven example (or a second example) with Testcontainers: PostgreSQL and Kafka.
2. Tag the integration tests `integration`.
3. Check that PIT skips them, and that the seeded faults measure them (`database` and `kafka` rulesets: "Seeded faults for this layer").
4. Show how to register an internal HTTP client library in `project.toml` (`extra_custom_assertion_regexes` and `extra_shallow_statement_regexes`). Use a small fake library in the example.

**Done when:** the hidden faults for the database and Kafka layers are detected, and the report shows it.

### Task 6: Multi-module Maven

1. Make the example (or a copy) a multi-module build.
2. Find the right `[commands]` overrides (`-pl <module> -am`). Check that `mutation` targets the module with the changed classes.
3. Document the result in `java-maven-junit5.md`.

### Task 7: Release preparation (do not publish)

1. Update `CHANGELOG.md`.
2. Run `python3 scripts/validate_repo.py`.
3. Ask the owner to review. Do not make the repository public. Do not publish to PyPI.

## 6. Rules for this work

1. Write all text in STE (`docs/writing-style.md`).
2. Keep the engine free of dependencies.
3. Each engine change needs a test in `engine/tests/test_cli.py`.
4. Run the tests and the validator before each commit.
5. Keep the versions equal in `engine/src/qestack/__init__.py`, `plugins/qestack/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (the validator checks this).
6. Do not change .NET files, except to keep the tests green.
7. Do not add the owner's employer code, names or data to the repository.
8. Do not make the repository public and do not publish packages.
9. Ask the owner before you change a decision in section 2.

## 7. File map

| Path | Content |
|---|---|
| `engine/src/qestack/cli.py` | All engine commands (one file) |
| `engine/src/qestack/data/defaults.toml` | Core defaults: paths, gates, weights, loop |
| `engine/src/qestack/data/stacks/java-maven-junit5.{toml,md}` | The Java stack (verify in task 3) |
| `engine/src/qestack/data/rulesets/*.md` | API, database, Kafka, UI rules for agents |
| `engine/src/qestack/data/rubrics/*.md` | Judge rubrics |
| `engine/src/qestack/data/templates/` | Files that `qestack init` and `qestack show` use |
| `engine/src/qestack/data/adapters/speckit/` | Speckit commands and constitution text |
| `engine/tests/test_cli.py` | End-to-end tests (fake test runner, no Maven) |
| `plugins/qestack/skills/*/SKILL.md` | The 10 skills |
| `plugins/qestack/agents/*.md` | The 4 agents |
| `plugins/qestack/hooks/hooks.json` | The guard hook |
| `.claude-plugin/marketplace.json` | Marketplace entry |
| `scripts/validate_repo.py` | Repository checks |
| `docs/PLAN.md` | Vision, roadmap, governance, risks |

## 8. Known issues

| Issue | Note |
|---|---|
| Lint is pattern based | False findings are possible. Registered helpers reduce them. |
| The hook fails open | On an internal error, the hook allows the action and prints a warning. CI is the authority. |
| Windows | Not supported in 0.1. The test fixtures use POSIX commands. |
| `qestack red` after the implementation | Not possible. Tests added in the harden loop are measured by mutation and seeded faults instead. |
| Speckit FR numbers restart in each feature | Handled by the feature tag (`feature-NNN`). |

## 9. Open questions for the owner

1. Is the employer open-source policy confirmed?
2. When to make the repository public?
3. Spring Boot in the example: now (task 3) or later (task 5)?
