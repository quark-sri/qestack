# Use qestack with other AI agents

The skills follow the open SKILL.md standard. The engine is a normal command-line tool. So the core of qestack works with other agents too. Claude Code gets the most complete experience in 0.1, because it also gets the four agents and the guard hook through the plugin.

| Feature | Claude Code | Codex CLI | Cursor | GitHub Copilot |
|---|---|---|---|---|
| Engine and gates | yes | yes | yes | yes |
| Skills | plugin | `~/.agents/skills` or `.agents/skills` | rules / skills | instructions / prompts |
| Separate sub-agents | plugin | partial | no | partial |
| Guard hook | plugin | no (use the CI guard) | no (use the CI guard) | no (use the CI guard) |

Status in 0.1: only Claude Code is tested. The other installs are planned for 0.2 with tested guides.

## Skills only (any agent that reads SKILL.md)

```bash
git clone https://github.com/quark-sri/qestack ~/qestack
scripts/install-skills.sh ~/.agents/skills      # or ~/.claude/skills, or <repo>/.agents/skills
```

The script makes symbolic links, so `git pull` updates the skills. To upload a skill to claude.ai or the Skills API, remove the `argument-hint` line first: outside Claude Code, that field is an error. It links all skills of the plugin. The library skills need no engine. The gated skills (`qestack`, `qe-*`) also need the engine. The reviewer personas are agent files in `plugins/qestack/agents/`. The script does not link them. Only the `test-review-panel` skill uses them. If your agent cannot start separate reviewers, the panel applies the checklists in one session and says that the review was not independent.

## Without sub-agents

Where an agent cannot start a separate sub-agent, run the role in a new session. Example for the judge: start a new session, give it the text of `plugins/qestack/agents/qe-test-judge.md`, and ask it to review the feature. For a review persona, give the new session the text of its file in `plugins/qestack/agents/`, for example `domain-oracle-reviewer.md`. A new session has no memory of writing the tests, so the review is still independent.

## Without the hook

Run `qestack guard --feature <feature>` after each agent session, and in CI. The guard finds weakened, skipped and deleted tests against the base branch and the lock.
