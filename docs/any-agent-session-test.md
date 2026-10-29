# Session test in other AI coding agents

`docs/library-session-test.md` checks the skills in Claude Code. This test checks the portable skill packages in other agents that read SKILL.md. The validator and CI check the files only. Only a real session shows if an agent finds, starts and follows the skills.

A person runs this test. Claude Code cannot start other agents. Record the result of each run in [Results](#results) in this file, with the date, the agent version and the model.

## First test set

| Agent | Why |
|---|---|
| Codex (CLI) | Reads `.agents/skills`. Has sub-agents. |
| Cursor | Reads `.agents/skills`. Has sub-agents. |
| GitHub Copilot CLI | Reads `.agents/skills`. Has custom agents. |
| Gemini CLI or Antigravity CLI | Reads `.agents/skills`. Use the one that your Google plan gives you: Antigravity CLI replaced Gemini CLI for the unpaid tier and Google One on 2026-06-18. |

The other agents of the tables in [other-agents.md](other-agents.md) come later: Copilot in VS Code, Devin Desktop, OpenCode and Cline.

## Setup (once for each agent)

Use a copy of the example project, so that the agent sees only that project and the qestack repository does not change.

```bash
cd <your qestack clone>
git pull
T=$(mktemp -d)/order-discount
cp -R examples/order-discount "$T"
cd "$T" && git init -q -b main && git add -A && git commit -qm "example" && cd -
scripts/install-skills.sh --agent <name> --project "$T" --copy
```

- `<name>`: `codex`, `cursor`, `copilot`, `gemini` or `antigravity`.
- `--copy` puts real folders into the project. Then the agent does not need access to your clone.
- For the gated check G1, install the engine: `pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"`.
- Start the agent in `$T`. Start a new session for each check group (S, R, G), so that one check does not change the next.
- After each run, write down the agent version and the model.

## Checks

### I: install

| ID | Do | Pass when |
|---|---|---|
| I1 | Ask: "which skills do you have?", or use the skill list of the agent | The agent lists the qestack skills, for example `testcase-reviewer`, `edge-case-hunter`, `qa-navigator` and `qestack` |
| I2 | In I1 | The agent shows no error about the skill files (frontmatter, unknown fields) |

### S: routing (from library-session-test S2, S3, S4, S7)

After each request, ask: "which skill did you use?". Also look in the session log for a read of the `SKILL.md` file.

| ID | Do | Pass when |
|---|---|---|
| S2 | Ask: "review the tests in this project" | `testcase-reviewer` starts, not `test-review-panel` |
| S3 | Ask: "what edge cases are missing in specs/001-order-discount/spec.md" | `edge-case-hunter` or `requirement-gaps` starts |
| S4 | Ask: "where do I start with testing this repository" | `qa-navigator` starts and proposes at most three skills |
| S7 | In S2 to S4 | No gated skill (`qestack`, `qe-*`) starts, although the project has a `.qestack/` folder |

### R: review panel

New session. Ask: "review the tests in this project with the test review panel. Do not run tests."

| ID | Do | Pass when |
|---|---|---|
| R1 | In the run | `test-review-panel` starts, chooses personas and says why |
| R2 | In the run | The agent starts each persona as a sub-agent, or it reads the persona texts in `references/personas/` of the skill and applies them one at a time |
| R3 | In the run | The report says "Independent: yes" only if each persona ran as a separate sub-agent. Else it says "Independent: no" |
| R4 | In the run | One merged, ranked list of findings, with a file and a line for each finding |
| R5 | In the run | It writes `qa-reviews/<date>-<scope>/` with `panel-report.md`, `findings.json` and `personas/<name>.md` |
| R6 | After the run | `git status` shows only `qa-reviews/`. The source files did not change |

Score R with the [answer key of library-session-test](library-session-test.md#answer-key-for-examplesorder-discount): the number of K1 to K14 in `panel-report.md`.

### G: gated workflow (needs the engine)

New session. Ask: "judge the tests of feature 001-order-discount with qestack".

| ID | Do | Pass when |
|---|---|---|
| G1 | In the run | `qe-judge` starts and does the preflight (`qestack --version`, `.qestack/project.toml`) |
| G2 | In the run | If the agent cannot start the `qestack:` agents, it stops at the judge step. It gives a text to paste into a new session, with the path of `qe-test-judge.md` and the start lines. It does not judge in the same session |
| G3 | In the run | It changed no test file |
| G4 | In a new, empty git repository, run `qestack init` | `AGENTS.md` has the qestack section between the `qestack:start` and `qestack:end` lines |
| G5 | After G4, start the agent there and ask: "which rules does this repository give you about tests?" | The agent names the qestack rules of `AGENTS.md`, for example no weakened locked tests and `qestack guard` before a commit |

G2 also passes if the agent starts the judge as a separate sub-agent with the agent text. Write down which way it took.

## Results

Write one row for each run. Result: pass, fail or partial for each group, and the check IDs that failed. Put the details of each failure in the last column.

| Date | Agent | Version | Model | I | S | R (K found) | G | Notes |
|---|---|---|---|---|---|---|---|---|
| | Codex | | | not run yet | | | | |
| | Cursor | | | not run yet | | | | |
| | GitHub Copilot CLI | | | not run yet | | | | |
| | Gemini CLI or Antigravity CLI | | | not run yet | | | | |
| | GitHub Copilot in VS Code | | | not run yet (later) | | | | |
| | Devin Desktop | | | not run yet (later) | | | | |
| | OpenCode | | | not run yet (later) | | | | |
| | Cline | | | not run yet (later) | | | | |
