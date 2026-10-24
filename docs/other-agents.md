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

The script makes symbolic links, so `git pull` updates the skills. It links the skills of both plugins. The `qe-skills` skills need no engine. The reviewer personas are files inside the `test-review-panel` skill, so they come with it. Only that skill uses them. If your agent cannot start separate reviewers, the panel applies the checklists in one session and says that the review was not independent.

## Without sub-agents

Where an agent cannot start a separate sub-agent, run the role in a new session. Example for the judge: start a new session, give it the text of `plugins/qestack/agents/qe-test-judge.md`, and ask it to review the feature. For a review panel persona, give the new session the text of `plugins/qe-skills/agents/test-reviewer.md` (or `test-saboteur.md` for a persona that changes code) and the persona file. A new session has no memory of writing the tests, so the review is still independent.

## Without the hook

Run `qestack guard --feature <feature>` after each agent session, and in CI. The guard finds weakened, skipped and deleted tests against the base branch and the lock.
