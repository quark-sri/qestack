# qestack

**qestack: skills, plugins and agents for AI Quality Engineering.**

AI coding agents now write code, tests, reviews and specs. qestack's goal is to build a growing toolbox — Claude Code skills, agents and measurable gates — that makes AI-assisted quality engineering trustworthy, not just fast.

The first capability, and the full scope of release 0.1, is **AI test quality**: proving that your AI-written tests catch bugs. AI agents write tests very fast. Many of these tests are green and give high coverage, but they do not find bugs. qestack gives your AI agent a process to write the right tests, and it measures the result with evidence, not with opinions. Later releases add more AI Quality Engineering skills beyond test quality (see the [roadmap](docs/PLAN.md#7-roadmap)).

> Status: **0.1 alpha, private review.** Release 0.1 supports Java with Maven and JUnit 5. The .NET stack is in the repository but is experimental and not supported in 0.1. Read [Limits](#limits) before you use it.

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

## Install

You need Python 3.11 or later, git, and Claude Code.

**1. The engine** (the `qestack` command):

```bash
pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"
```

**2. The Claude Code plugin** (skills, agents and the guard hook). In Claude Code:

```
/plugin marketplace add quark-sri/qestack
/plugin install qestack@qestack
```

**3. Your repository:**

```bash
cd your-repo
qestack init            # add --speckit if you use GitHub Spec Kit
qestack doctor
```

Then, in Claude Code, run `/qe-setup` to finish the configuration (assertion helpers, build commands, thresholds).

Other agents (Codex, Cursor, Copilot): the skills follow the open SKILL.md standard. See [docs/other-agents.md](docs/other-agents.md).

## Supported

| Stacks (exactly one) | Rulesets (zero or more) |
|---|---|
| `java-maven-junit5`: Java, Maven, JUnit 5, PIT | `api-http`: any HTTP client, including internal libraries |
| `dotnet` (experimental, not supported in 0.1) | `database`: persisted state, constraints, transactions |
| | `kafka`: producers, consumers, keys, headers, idempotency, DLQ |
| | `ui-playwright`: Playwright for Java and .NET |

Planned: .NET (full support), Java with Gradle, TypeScript (Vitest, Jest), Python (pytest). See the [roadmap](docs/PLAN.md#7-roadmap).

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
- **Check the build commands once by hand.** Plugin property names can differ between versions.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md). All documentation and prompts use [Simplified Technical English](docs/writing-style.md).

## License

[Apache License 2.0](LICENSE)
