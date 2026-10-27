# qestack

**qestack: QA and test automation skills, agents and quality gates for AI coding agents.**

One Claude Code plugin with two parts: a QA library of 39 Quality Engineering skills and 8 reviewer personas for any stack, and a gated workflow with an engine that proves AI-written tests catch bugs. The skills follow the open [Agent Skills](https://agentskills.io) standard, so they also work in other AI coding agents: Codex, Cursor, GitHub Copilot, Gemini CLI and more (see [Install](#install), option C).

AI coding agents now write code, tests, reviews and specs. qestack's goal is to build a growing toolbox — Claude Code skills, agents and measurable gates — that makes AI-assisted quality engineering trustworthy, not just fast.

The first capability, and the full scope of release 0.1, is **AI test quality**: proving that your AI-written tests catch bugs. AI agents write tests very fast. Many of these tests are green and give high coverage, but they do not find bugs. qestack gives your AI agent a process to write the right tests, and it measures the result with evidence, not with opinions. Later releases add more AI Quality Engineering skills beyond test quality (see the [roadmap](docs/PLAN.md#7-roadmap)).

> Status: **0.1 alpha, owner review.** Release 0.1 supports Java with Maven and JUnit 5. The .NET stack is in the repository but is experimental and not supported in 0.1. Read [Limits](#limits) before you use it.

## Why

Coverage shows that a line **ran**. A green build shows that no assertion **failed**. Neither shows that the tests can **detect a defect**.

Typical problems with AI-written tests:

- The agent writes tests from the code, so the tests confirm the bugs.
- Tests check only "not null" or the HTTP status.
- Some requirements have no tests. Negative and boundary cases are missing.
- The agent deletes or weakens tests to get a green build.
- The agent that wrote the tests also says that they are good.

## What qestack does today (release 0.1: AI test quality)

| Step | Skill | Evidence |
|---|---|---|
| Check the spec | `/qe-grill-spec` | Each requirement has an ID, an example and a defined error behavior |
| Design tests from the spec | `/qe-plan` | `test-plan.md` with a traceability table, reviewed by an independent judge |
| Write tests without the implementation | `/qe-write` | Lint gate (no hollow, assertion-free or skipped tests) and trace gate (100% of requirements) |
| Prove that the tests fail first, then lock them | `/qe-prove` | Red-before-green; a hook blocks later edits that weaken the tests |
| Harden the tests | `/qe-harden` | Mutation score, hidden realistic faults, flakiness, guard, judge, Test Quality Score |
| Measure an existing suite | `/qe-audit` | A read-only report with numbers |
| Check the judge | `/qe-calibrate` | Agreement and Cohen's kappa against human verdicts |

The result of each feature is `specs/<feature>/quality-report.md` with the decision **ACCEPT** or **ESCALATE**. A human reads the report and a small audit sample, not every line of test code.

## QA library for any project (no engine needed)

The qestack plugin also has a library of 39 Quality Engineering skills and 8 reviewer personas. They work in any repository, with any language and any test framework, and they need no engine. Only the gated workflow (`qestack` and the `qe-*` skills) needs the engine. Without the engine, these skills tell you how to install it and stop.

- **Method first.** Each `SKILL.md` gives the QE method: objective, discovery questions, principles, workflow, anti-patterns and a "Done when" checklist. It names no tools.
- **Stack recipes on demand.** Tool details live in `references/` (Java, TypeScript and JavaScript, Python). A skill reads only the recipe for the project's stack.
- **One shared context.** `qa-project-context` writes `.agents/qa-project-context.md` once (stack, test commands, CI, environments, risks). Every other skill reads it first.
- **Reviewer personas.** Eight agents, each with one job, a checklist, an evidence rule (file and line) and no edit tools. Personas find and report; they never change a file. The caller changes code. Start one directly, use them in your own skills, or let `test-review-panel` run several and merge their findings into one ranked list. The other skills of this plugin stay self-contained and do not depend on the personas.
- **Clear routing.** Each description is short, in the third person, and says what the skill does, "Use when" and "Not for". `qa-navigator` routes a request that fits no skill clearly. The skills follow the Claude standards for skills and agents ([guide](docs/guides/adding-a-skill.md)).

| Category | Skills |
|---|---|
| Foundation | `qa-project-context`, `qa-navigator` |
| Strategy | `test-strategy`, `test-planning`, `risk-based-testing`, `requirement-gaps`, `testability-review`, `exploratory-testing` |
| Design | `test-case-designer`, `edge-case-hunter` |
| Automation | `unit-testing`, `api-testing`, `database-testing`, `messaging-testing`, `contract-testing`, `ui-automation`, `service-virtualization`, `test-data-management` |
| Infrastructure | `test-environments`, `ci-cd-integration` |
| Non-functional | `performance-testing`, `security-testing`, `accessibility-testing`, `localization-testing`, `resilience-testing` |
| Test quality | `testcase-reviewer`, `test-review-panel`, `test-coverage-map`, `mutation-probe`, `flaky-test-detective` |
| Code and spec | `bug-hunter`, `roast-my-code`, `spec-drift` |
| Run and triage | `test-runner`, `change-impact`, `bug-report` |
| Process | `release-readiness`, `production-testing`, `quality-postmortem` |

| Persona | Agent | Finds |
|---|---|---|
| AI Behavior Auditor | `ai-behavior-auditor` | shortcuts to green: copied expected values, tautologies, sycophancy, weaker assertions, skips, test-only code, false 'all pass' claims |
| Hallucination Checker | `hallucination-checker` | APIs, fixtures, properties, flags, paths and versions that do not exist |
| Domain Oracle Reviewer | `domain-oracle-reviewer` | wrong expected results, misread or invented rules, missing negative and error cases |
| Saboteur | `saboteur` | faults that the tests would not catch (it designs a fault plan; the caller runs it) |
| Test Automation Architect | `test-automation-architect` | wrong test level, pyramid shape, page objects, helpers, data and pipeline fit |
| Determinism and Flakiness Engineer | `determinism-flakiness-engineer` | sleeps, real clock, unseeded random data, shared state, order, retries |
| Maintainability Craftsperson | `maintainability-craftsperson` | names, duplication, mystery data, hidden assertions, over-mocking, failure messages |
| Suite Cost and Speed Reviewer | `suite-cost-speed-reviewer` | slow tests at the wrong level, repeated setup, parallel runs, pipeline cost |

**Use one persona.** Ask for it by name, for example "use the domain-oracle-reviewer agent on src/test/orders". In Claude Code, `/agents` lists them.

**How the review panel works.** Ask for a panel review, for example "review the tests in this pull request with the panel". To choose the personas: `/qestack:test-review-panel src/test/orders --personas domain-oracle-reviewer,saboteur`.

1. The panel chooses the personas for the work. AI-written work always gets the AI Behavior Auditor and the Hallucination Checker.
2. The personas run in parallel. None of them has an edit tool. The Saboteur returns a fault plan: the exact change for each fault, and a prediction.
   After all reports, the panel runs the fault plan with the `mutation-probe` method. It works in an isolated copy, one fault at a time, and marks each prediction as proven or wrong.
3. Each persona gets the same brief. A persona does not see the other reports.
4. The panel checks the evidence for each blocker and major finding. It merges duplicates and gives one ranked list with a verdict.
5. The reviewers only return their reports. The panel saves the run in `qa-reviews/<date>-<scope>/`: `panel-report.md` for people, `findings.json` for pipelines and trends, and `personas/<name>.md` with each full report. It can also offer to publish the report as a page or a pull request comment.

**Write your own persona.** The personas are in [`plugins/qestack/agents/`](plugins/qestack/agents/). Copy one, and keep three things:

- the "Reviewer rules" section unchanged, so that your persona returns the same findings block
- the sections Scope, Checklist, Method, Evidence rule, Output and Limits
- read tools only, plus command access if the job must run read-only commands or tests; never an edit tool

To add it to the panel, add a row to the table in `test-review-panel`. The validator checks the sections, the shared rules, the tools and the table.

To install the library alone, see [Install](#install), option A, or option C for other agents. [`llms.txt`](llms.txt) lists every skill and agent in one file, for AI agents and skill registries.

Use the gated qestack workflow below when you want measured proof for each feature: test locks, hidden faults, mutation gates and an independent judge.

## Install

Choose one option. Option A gives you the library skills and the personas in Claude Code. Option B adds the engine, which the gated workflow (`qestack` and the `qe-*` skills) needs. Option C installs the skills in other AI coding agents.

**Option A: the library only (no engine, no Python).** In Claude Code:

```
/plugin marketplace add quark-sri/qestack
/plugin install qestack@qestack
```

From a clone, `scripts/install.sh --skills-only` does the same. The gated skills are in the plugin too. Without the engine, they tell you how to install it and stop. For other agents, see option C.

**Option B: the library and the gated workflow.** You need Python 3.11 or later, git, pipx (or uv), and Claude Code. Two commands: the first installs the engine and the Claude Code plugin, the second sets up your repository.

```bash
git clone https://github.com/quark-sri/qestack && qestack/scripts/install.sh
cd your-repo && qestack init --existing    # drop --existing for a new project; add --speckit for GitHub Spec Kit
```

`qestack init` detects the stack and the rulesets, creates `.qestack/`, shows a lint preview of your existing tests and prints the next steps. `--existing` starts with lower mutation and seed thresholds. `--hook` adds the guard hook to `.claude/settings.json` (only needed without the plugin). Then run `qestack doctor`, and `/qe-setup` in Claude Code to check the assertion helpers and the build commands.

**Manual install of option B** (the same steps, one by one):

```bash
pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"
```

In Claude Code:

```
/plugin marketplace add quark-sri/qestack
/plugin install qestack@qestack
```

**Option C: use with any AI coding agent.** Each agent reads skills from a skill folder. Most agents share one folder:

| Agent | Project folder | User folder |
|---|---|---|
| Codex, Cursor, GitHub Copilot (CLI and VS Code), Gemini CLI, Devin Desktop (was Windsurf), OpenCode | `.agents/skills/` | `~/.agents/skills/` |
| Antigravity | `.agents/skills/` | see [other agents](docs/other-agents.md#skill-folders) |
| Claude Code without the plugin | `.claude/skills/` | `~/.claude/skills/` |
| Cline | `.cline/skills/` | `~/.cline/skills/` |

Link the skills into the folder of your agent:

```bash
git clone https://github.com/quark-sri/qestack ~/qestack
~/qestack/scripts/install-skills.sh ~/.agents/skills     # or another folder from the table
```

The links point to the clone, so `git pull` updates the skills.

To upload skills to a host that accepts only the fields of the Agent Skills standard, use the portable packages. claude.ai and the Skills API are such hosts. Run `python3 scripts/build_skills.py` in the clone. It writes `dist/`: one zip for each skill, a bundle of all 49 skills and a bundle of the 39 library skills.

What works outside Claude Code in release 0.1:

- **Library skills:** need no engine. Each agent that reads SKILL.md can use them.
- **Gated skills:** also need the engine, git and a shell. Install the engine with the `pipx` command of the manual install above.
- **Review panel:** if the agent cannot start separate reviewers, the panel does the reviews in one session. The report then says that the review was not independent. The portable packages do not contain the reviewer texts yet; a later step adds them.
- **Guard hook:** only in Claude Code. In other agents, run `qestack guard` in CI.

Only Claude Code is tested in 0.1. The folders come from the official documentation of each agent (checked on 2026-10-27). [docs/other-agents.md](docs/other-agents.md) has the sources, the sub-agent and hook support of each agent, and the steps without sub-agents.

## Supported

| Stacks (exactly one) | Rulesets (zero or more) |
|---|---|
| `java-maven-junit5`: Java, Maven, JUnit 5, PIT | `api-http`: any HTTP client, including internal libraries |
| `java-gradle-junit5`: Java, Gradle, JUnit 5, PIT | `database`: persisted state, constraints, transactions |
| `dotnet` (experimental, not supported in 0.1) | `kafka`: producers, consumers, keys, headers, idempotency, DLQ |
| | `ui-playwright`: Playwright for Java and .NET |

Planned: .NET (full support), TypeScript (Vitest, Jest), Python (pytest). See the [roadmap](docs/PLAN.md#7-roadmap).

## How it works

```
spec.md ─► /qe-plan ─► test-plan.md ─► /qe-write ─► tests ─► /qe-prove ─► red + lock
                                                                             │
                                          (you or your agent implement the feature)
                                                                             │
quality-report.md ◄─ score ◄─ judge ◄─ gates (mutation, hidden faults, …) ◄─ /qe-harden
        │                                         ▲
        └── CONTINUE: specific feedback ──► writer improves the tests ──┘
```

Four agents with separate roles do the work:

| Agent | Job | Must not |
|---|---|---|
| `qe-test-designer` | Test plan from the spec | Read the implementation |
| `qe-test-writer` | Tests from the plan | Read the implementation; change production code; weaken tests |
| `qe-test-judge` | Independent review with a rubric and file:line evidence | Change any code |
| `qe-fault-seeder` | Hidden realistic faults as patches | Change tests; tell the writer about the faults |

See it on a real build: [`examples/order-service-maven`](examples/order-service-maven/) runs every gate with Maven, Surefire, Failsafe and PIT, and shows the real numbers for a weak AI-written test class.

Read more: [why qestack and the metrics](docs/why-qestack.md), [architecture](docs/architecture.md), [configuration](docs/configuration.md).

## The gates

| Gate | Question | Default |
|---|---|---|
| trace | Does every required requirement have a test? | 100% |
| hollow / no_assertion / skipped | Is there a test that checks nothing? | 0 |
| red | Did each new test fail before the feature existed? | 100% |
| flaky / failing | Are the results stable and green? | 0 |
| mutation | Do the tests kill mutants in the changed code? | ≥ 75% |
| seed | Do the tests detect hidden realistic faults? | ≥ 90% |
| guard | Did anything weaken tests or change protected files? | 0 |
| judge | Did the independent judge reject a test? | 0 |
| TQS | Weighted Test Quality Score | ≥ 80 |

All values are in `.qestack/project.toml`. Start lower on an existing codebase.

## Limits

- **Lint is pattern based**, not a compiler. Register your assertion helpers. Mutation testing and the judge cover the gaps.
- **Hooks help, but they are not security.** A shell trick can bypass them. The CI guard against the base branch is the authority. Use CODEOWNERS for `.qestack/`.
- **Mutation testing is slow** on tests that start containers. The Java stack excludes the `integration` and `ui` tags from PIT. Hidden faults measure those tests.
- **The judge is a model.** Calibrate it each sprint with `/qe-calibrate`.
- **Check the build commands once by hand.** The Java commands are verified with Surefire and Failsafe 3.6.0 and PIT 1.30.1. Other plugin versions can use other property names.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md). All documentation and prompts use [Simplified Technical English](docs/writing-style.md).

## Acknowledgements

The skill structure, the description routing and the shared context convention (`.agents/qa-project-context.md`) of the qestack QA library are inspired by [petrkindlmann/qa-skills](https://github.com/petrkindlmann/qa-skills) (MIT). The text in this repository is our own.

## License

[Apache License 2.0](LICENSE)
