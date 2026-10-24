# qestack project plan

| | |
|---|---|
| Status | Draft for owner review |
| Owner | quark-sri |
| Version | 0.1 (plan for releases 0.1 to 1.0) |
| Writing standard | Simplified Technical English (see `docs/writing-style.md`) |

## 1. Vision

AI coding agents now write code, tests, reviews and specs. qestack's purpose is to build a growing toolbox of Claude Code skills, agents and gates for **AI Quality Engineering**: making AI-assisted quality work trustworthy, not just fast.

Release 0.1 ships the first capability. AI agents can write many tests very fast. Many of these tests look correct, but they do not find bugs. Coverage and pass rates do not show this problem. qestack gives AI agents a process to write the right tests, and it proves, with objective evidence, that the tests find bugs. Later releases (section 7) add more AI Quality Engineering skills beyond test quality: for example spec review, code review for testability, and bug triage.

**One-line description:** qestack: skills, plugins and agents for AI Quality Engineering. Release 0.1: gates that prove your AI-written tests catch bugs.

## 2. The problem

1. Agents write tests from the code, not from the requirements. The tests confirm the current behavior, including its bugs.
2. Agents write weak tests: empty bodies, "not null" checks, status-only checks.
3. Agents skip requirements, negative cases and boundary cases.
4. Agents weaken or delete tests to get a green build.
5. The agent that writes the tests also says that they are good.
6. Humans cannot read every line that agents write.

## 3. Positioning

| Other projects | qestack |
|---|---|
| Help AI write more tests | Proves that the tests catch bugs |
| Use coverage as the target | Uses mutation score and hidden faults as the target |
| Let the writer review its own work | Uses an independent judge with a rubric and evidence |
| Trust the agent not to cheat | Locks tests and blocks weakening edits |
| Focus on JavaScript and UI | Starts with Java (Maven, JUnit 5), API, database and Kafka; adds more stacks later |

Related projects (see `docs/landscape.md`): Agentic QE, qa-skills, claude-qa-automation, Playwright Test Agents, TDD Guard, Mutahunter, Meta ACH (research). None of them combines all the qestack gates.

## 4. Principles

1. **Evidence over opinion.** A claim about test quality needs a number from a gate or a file and line from the judge.
2. **Spec first.** Tests come from the requirements. The test writer does not read the implementation.
3. **Separate roles.** The designer, writer, judge and fault seeder are different agents with different context.
4. **Small, composable skills.** Each skill does one job and works alone. One skill chains them for the full loop.
5. **Engineer in control.** qestack proposes. The human decides on exclusions, equivalent mutants and test defects.
6. **No lock-in.** Skills follow the open SKILL.md standard. The engine is a plain command-line tool. Speckit is optional.
7. **Honest limits.** Documentation states what the tool cannot do.
8. **Plain language.** All documentation and prompts use Simplified Technical English.

## 5. Architecture

```
qestack/                              (this repository)
  .claude-plugin/marketplace.json     Claude Code marketplace entry
  plugins/qestack/
    .claude-plugin/plugin.json        plugin manifest
    skills/                           SKILL.md files (also usable by Codex, Cursor, Copilot)
    agents/                           designer, writer, judge, fault seeder
    hooks/hooks.json                  test-lock guard
  engine/                             Python package "qestack" (command-line tool)
    src/qestack/cli.py                all gates
    src/qestack/data/                 defaults, stacks, rulesets, rubrics, templates, adapters
    tests/                            unit tests (standard library only)
  examples/                           sample projects
  benchmarks/                         real-bug evaluation (planned)
  docs/                               plan, guides, analysis, landscape, writing style
```

In a user repository, qestack keeps its files in one folder:

```
.qestack/
  project.toml        project settings (protected)
  project-rules.md    project guidance for agents (protected)
  runs/<feature>/     gate results; some files are committed
  locks/              test locks and human decisions (protected, committed)
```

### 5.1 Configuration model

| Level | Name | Example | Rule |
|---|---|---|---|
| 1 | Core defaults | `data/defaults.toml` | Ships with the engine |
| 2 | Stack | `java-maven-junit5` (`dotnet` is experimental) | Exactly one |
| 3 | Rulesets | `api-http`, `database`, `kafka`, `ui-playwright` | Zero or more |
| 4 | Project settings | `.qestack/project.toml` | One per repository |

A later level overrides an earlier level. `extra_<key>` appends to a list.

### 5.2 Why Python for the engine

- Zero dependencies (standard library only, Python 3.11 or later).
- Java and .NET teams usually have Python on build machines.
- The engine is already tested.
- Install with `pipx install qestack` or `uv tool install qestack`.

## 6. Skill catalog (release 0.1)

| Skill | Slash command | Job |
|---|---|---|
| qestack | `/qestack` | Entry point. Explains qestack and routes to the right skill |
| qe-setup | `/qe-setup` | Detect the stack, choose rulesets, register assertion helpers, check the build |
| qe-grill-spec | `/qe-grill-spec` | Find unclear or untestable requirements before test design |
| qe-plan | `/qe-plan` | Spec-first test plan with traceability and an independent plan review |
| qe-write | `/qe-write` | Blind test writing with lint and trace gates |
| qe-prove | `/qe-prove` | Red-before-green check, then lock the tests |
| qe-harden | `/qe-harden` | Hidden faults, mutation testing, judge and improvement loop |
| qe-judge | `/qe-judge` | Independent review only |
| qe-audit | `/qe-audit` | Read-only quality report for an existing test suite |
| qe-calibrate | `/qe-calibrate` | Compare judge verdicts with human verdicts |

**Typical flow:** `/qe-grill-spec` → `/qe-plan` → `/qe-write` → `/qe-prove` → (implement) → `/qe-harden`

**Speckit adapter:** `qestack init --speckit` adds `/speckit.testplan`, `/speckit.testwrite` and `/speckit.testquality`, which call the same skills.

### 6.1 QE skills for any project (plugin `qe-skills`)

35 skills for QA disciplines across the SDLC, and 8 reviewer personas (agents). They need no engine and no `.qestack/` folder.

| Rule | How |
|---|---|
| Tool-neutral method | `SKILL.md` names no tools; the validator checks this |
| Stack recipes | `references/java.md`, `typescript.md`, `python.md`, loaded only for the project's stack |
| Shared context | `.agents/qa-project-context.md`, written by `qa-project-context`, read by every skill |
| Routing | Each description has "Use when", "Not for" and "Related"; the validator checks that related skills exist |
| Personas | One agent per persona, with no edit tools (personas report; the caller changes code), a checklist, an evidence rule and one shared "Reviewer rules" section; only `test-review-panel` uses them, so the other skills stay self-contained; the validator checks this |
| Structure | Objective, Context, Discovery questions, Principles, Workflow, Anti-patterns, Done when, Related skills |

Categories: foundation, strategy, design, automation, infrastructure, non-functional, test quality, code and spec, run and triage, process. See the README for the full list.

Candidates for later releases: `mobile-testing`, `visual-testing`, `resilience-testing`, `observability-driven-testing`, `test-suite-curation`, `qa-metrics`, `ai-feature-testing`, and recipes for .NET and Go.

## 7. Roadmap

| Release | Target | Scope |
|---|---|---|
| 0.1 | Week 1–4 | Engine, plugin, 10 skills, 4 agents, hook. Stack: Java/Maven/JUnit 5 only. Rulesets: API, database, Kafka, Playwright UI. Speckit adapter. Docs. CI. A runnable Maven example. The `qe-skills` plugin. Owner review. |
| 0.2 | Week 5–8 | Stacks: .NET (full support), Java/Gradle, TypeScript (Vitest/Jest), Python (pytest). Install guides for Codex, Cursor, Copilot. Runnable example projects. PyPI release. Public launch. |
| 0.3 | Week 9–14 | Defects4J benchmark. LLM equivalent-mutant check. Judge calibration dataset. HTML report. |
| 0.4 | Week 15–20 | Rulesets: contract testing (Pact), security, gRPC, GraphQL. Gate results as SARIF for code scanning. |
| 1.0 | Month 6 | Stable configuration schema. Stable result file formats. Contributor guide for stacks and rulesets proven by outside contributions. |

## 8. Benchmark plan (release 0.3)

The benchmark is the main proof for the project.

1. Take 30 to 50 real bugs from [Defects4J](https://github.com/rjust/defects4j). Each bug has a buggy version, a fixed version and a description.
2. For each bug, write a short requirement from the bug report and the fixed behavior.
3. Arm A: an agent writes tests with a plain prompt.
4. Arm B: an agent writes tests with qestack (`/qe-plan`, `/qe-write`, `/qe-harden`).
5. Run both test sets against the buggy version.
6. Measure: bugs detected, mutation score, hollow and trivial test rate, agent cost and time.
7. Publish the method, the raw results and the scripts. Publish negative results too.

## 9. Launch plan (release 0.2)

1. Owner review. The repository is already public (owner decision, 2026-10-24).
2. Publish to PyPI.
3. Short demo: an AI-written suite with 100% coverage misses three planted bugs; qestack finds the gaps and the improved tests catch the bugs.
4. Blog post: "Coverage is not evidence: measuring AI-written tests".
5. Submit to awesome-claude-code, the Claude Code plugin marketplaces and the skills registries.
6. Announce on LinkedIn and in QA communities.

## 10. Governance

| Topic | Decision |
|---|---|
| License | Apache-2.0 |
| Maintainer | quark-sri (single maintainer for 0.x) |
| Contributions | Pull requests with tests. Stacks and rulesets follow the contributor guides. |
| Decisions | Issues with the label `proposal`. The maintainer decides in 0.x. |
| Versioning | Semantic versioning. Result file formats get a `schema` field. |
| Code of conduct | Contributor Covenant (link in `CODE_OF_CONDUCT.md`) |
| Security | Private reports through GitHub security advisories (`SECURITY.md`) |

## 11. Success metrics for the project

| Metric | Target at 1.0 |
|---|---|
| Benchmark: bugs detected, qestack vs plain prompt | Clear, published improvement |
| Judge agreement with humans (kappa) | ≥ 0.7 on the calibration dataset |
| Stacks supported | 5 or more |
| Outside contributors | 5 or more |
| GitHub stars | Signal only, not a target |

## 12. Risks

| Risk | Control |
|---|---|
| Employer intellectual property | Owner confirms the employer open-source policy before the public release. The repository contains no employer code or data. |
| Name confusion with Qt "QStack" | Always write "qestack AI test quality" in descriptions and package metadata. |
| Mutation testing is slow | Changed code only; exclude container tests; seeded faults for slow layers. |
| The judge is wrong | Calibration with human audits; the judge only proposes on equivalent mutants and test defects. |
| Hooks can be bypassed | CI guard against the base branch is the authority. Document this. |
| Pattern-based lint gives false findings | Registered assertion helpers; the judge and mutation score cover the gaps. |
| Benchmark shows no benefit | Publish the result and improve the method. Honest results build trust. |

## 13. Open decisions for the owner

1. Confirm the name `qestack` and the repository `quark-sri/qestack`.
2. Confirm the employer open-source policy.
3. Choose the public launch date.
4. Choose whether to publish to PyPI before or at the public launch.
