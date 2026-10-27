# Architecture

qestack has three parts:

1. **Engine:** the `qestack` command. It runs all gates and writes the result files. It has no AI in it.
2. **Plugin:** skills, agents and a hook for Claude Code. The agents do the AI work. The skills tell the main agent which engine commands and which agents to use, in which order.
3. **Project folder:** `.qestack/` in your repository. It holds your settings, the gate results and the test locks.

```
┌────────────── Claude Code ──────────────┐        ┌──────── your repository ────────┐
│ skills: /qe-plan, /qe-write, ...        │        │ specs/<feature>/spec.md         │
│ agents: designer, writer, judge, seeder │──────► │ specs/<feature>/test-plan.md    │
│ hook:   qestack hook (PreToolUse)       │        │ src/ ... tests ...              │
└───────────────┬─────────────────────────┘        │ .qestack/project.toml           │
                │ runs                              │ .qestack/project-rules.md       │
                ▼                                   │ .qestack/runs/<feature>/*.json  │
┌──────── qestack engine ────────┐   reads/writes  │ .qestack/locks/<feature>.json   │
│ lint trace red flaky mutation  │ ───────────────►└─────────────────────────────────┘
│ fault seed guard lock score    │
│ feedback calibrate init doctor │──► your build tool (Maven, dotnet), PIT, Stryker.NET
└────────────────────────────────┘
```

## Why the engine has no AI

- Gates must be deterministic. The same input gives the same result.
- CI can run the gates without an AI service.
- The AI cannot change its own grades. The engine computes the gates and the verdict rules.

The only AI-made input to the score is `judge.json`. The engine checks it: each score needs file:line evidence, each test in scope needs an entry, and the engine applies the verdict rules again. It uses the stricter verdict.

## Configuration levels

| Level | Where | Who changes it |
|---|---|---|
| Core defaults | `engine/src/qestack/data/defaults.toml` | qestack maintainers |
| Stack | `data/stacks/<name>.toml` and `.md`, or `.qestack/stacks/` | maintainers, or the project for a local stack |
| Rulesets | `data/rulesets/<name>.toml` and `.md`, or `.qestack/rulesets/` | maintainers, or the project |
| Project settings | `.qestack/project.toml` and `.qestack/project-rules.md` | the project team (human review) |

`.toml` files are settings for the engine. `.md` files are guidance for the agents. `qestack context` gives the agents the list of guidance files for the project.

## Result files

All result files for one feature are in `.qestack/runs/<feature>/`.

| File | Written by | Committed |
|---|---|---|
| `lint.json` | `qestack lint` | no |
| `trace.json`, `trace-plan.json` | `qestack trace` | no |
| `red.json` | `qestack red` | yes (CI cannot re-run the red check) |
| `flaky.json` | `qestack flaky` | no |
| `mutation.json` | `qestack mutation` | no |
| `faults/` | `qestack fault` | no (hidden from later agent sessions) |
| `seed.json` | `qestack seed` | no (contains fault details) |
| `seed-feedback.json` | `qestack seed` | yes (redacted) |
| `guard.json` | `qestack guard` | no |
| `plan-review.json`, `judge.json` | judge agent | yes |
| `judge-basis.json` | `qestack score` | yes (detects tests changed after the review) |
| `scorecard.json`, `history.jsonl` | `qestack score` | yes |
| `feedback-<n>.md` | `qestack feedback` | no |
| `human-audit.json`, `calibration.json` | human, `qestack calibrate` | yes |
| `suspected-bugs.md`, `suspected-test-defects.md` | writer agent | yes |

The report is also copied to `specs/<feature>/quality-report.md`.

The engine result files and the lock files have a `schema` field. A file without the field is schema 1. When a reader must change, raise `RESULT_SCHEMA` in the engine and read the older schema too. The engine refuses a file with a newer schema, so an old engine cannot misread it. For a lock file, the hook then blocks edits to test files. The engine writes each JSON file to a temporary file and then renames it, so a stopped run leaves no half-written file.

## Feature scope

Speckit numbers requirements again in each feature (`FR-001` in each feature). So each test also has a feature tag, for example `feature-003`. The engine uses the feature tag to find the tests of one feature. The feature name comes from `--feature`, from the environment (`QESTACK_FEATURE`, `SPECIFY_FEATURE`, `GITHUB_HEAD_REF`), or from the git branch name.

## The guard

The guard has three layers:

1. **Agent rules.** Each agent prompt has a "Forbidden" section.
2. **Hook.** `qestack hook` runs before each Edit, Write and Bash call in Claude Code. It finds the qestack project from the edited file (or from the session folder for Bash), so it also works when the session starts at the root of a monorepo. It blocks changes to protected files. For locked test files, it computes the file after the edit and blocks the edit if a test is removed, an assertion is removed or weaker, a skip is added, or a requirement tag is removed.
3. **CI.** `qestack guard` compares the tests with the base branch and with the lock. CI is the authority, because a hook can be bypassed.

## Test parsing

The engine does not compile code. It masks comments and string literals, then finds test methods with the stack regexes and matches braces. This is fast and works for Java and C#. It can miss unusual code. The mutation score and the judge cover these gaps.
