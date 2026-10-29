# Use qestack with other AI agents

The skills follow the open SKILL.md standard. The engine is a normal command-line tool. So the core of qestack works with other agents too. Claude Code gets the most complete experience in 0.1, because the plugin also gives it the 4 workflow agents, the 8 reviewer personas and the guard hook.

The tables below come from the official documentation of each agent. Each row has a source link and the date of the check. "Not documented" means that the source does not say. It does not mean "no". The full list of agents that read SKILL.md is the [agentskills.io client showcase](https://agentskills.io/clients). The tables cover a selection of coding agents from that list.

### Skill folders

| Agent | Project folder | User folder | Reads `.agents/skills` | Unknown frontmatter keys (such as `argument-hint`) | Source | Checked on |
|---|---|---|---|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | not documented | Ignored without an error. Upload to claude.ai or the Skills API fails on a key outside the spec. | [skills](https://code.claude.com/docs/en/skills) | 2026-10-27 |
| Codex (CLI, app) | `.agents/skills/` in each folder from the working folder up to the repository root | `~/.agents/skills/` (admin: `/etc/codex/skills`) | yes | not documented | [build skills](https://learn.chatgpt.com/docs/build-skills) | 2026-10-27 |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | yes | not documented | [skills](https://cursor.com/docs/context/skills) | 2026-10-27 |
| GitHub Copilot CLI | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` | yes | not documented | [add skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | 2026-10-27 |
| GitHub Copilot in VS Code | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | yes | not documented. VS Code reads `argument-hint`. | [agent skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) | 2026-10-27 |
| Gemini CLI | `.gemini/skills/`, `.agents/skills/` | `~/.gemini/skills/`, `~/.agents/skills/` | yes (it has priority over `.gemini/skills/`) | not documented | [skills](https://geminicli.com/docs/cli/skills/) | 2026-10-27 |
| Antigravity (CLI, IDE) | `.agents/skills/` (old: `.agent/skills/`) | CLI: `~/.gemini/antigravity-cli/skills/`. IDE: `~/.gemini/config/skills/` | project: yes. User: not documented | not documented | [skills](https://antigravity.google/docs/skills) | 2026-10-27 |
| Devin Desktop (was Windsurf), Devin Local agent | `.agents/skills/`, `.devin/skills/`, `.windsurf/skills/` | `~/.agents/skills/`, `~/.config/devin/skills/` | yes | not documented | [Devin Local](https://docs.devin.ai/desktop/devin-local), [skills](https://docs.devin.ai/cli/extensibility/skills/overview) | 2026-10-27 |
| Cline | `.cline/skills/`, `.clinerules/skills/`, `.claude/skills/` | `~/.cline/skills/` | not documented | not documented | [skills](https://docs.cline.bot/customization/skills) | 2026-10-27 |
| OpenCode | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | yes | Ignored. | [skills](https://opencode.ai/docs/skills/) | 2026-10-27 |

### Sub-agents and hooks

The qestack workflow agents and the reviewer personas need separate sub-agents. The qestack guard hook needs a hook that runs before a file edit and can block it.

| Agent | Sub-agents: folders and file format | Hooks: file and event before a tool call | Source | Checked on |
|---|---|---|---|---|
| Claude Code | `.claude/agents/`, `~/.claude/agents/`. Markdown with YAML frontmatter. | `.claude/settings.json`, `~/.claude/settings.json` or a plugin `hooks/hooks.json`. `PreToolUse` can block. | [sub-agents](https://code.claude.com/docs/en/sub-agents), [hooks](https://code.claude.com/docs/en/hooks) | 2026-10-27 |
| Codex (CLI, app) | `.codex/agents/`, `~/.codex/agents/`. One TOML file for each agent (`name`, `description`, `developer_instructions`). | `.codex/hooks.json` or `config.toml`, also in `~/.codex/`. `PreToolUse` can deny, also for `apply_patch` edits. A project hook runs only after the user trusts it. | [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [hooks](https://learn.chatgpt.com/docs/hooks) | 2026-10-27 |
| Cursor | `.cursor/agents/`, `~/.cursor/agents/`. Also reads `.claude/agents/` and `~/.claude/agents/`. Markdown with YAML frontmatter. | `.cursor/hooks.json`, `~/.cursor/hooks.json`. `preToolUse` can deny. | [subagents](https://cursor.com/docs/context/subagents), [hooks](https://cursor.com/docs/agent/hooks) | 2026-10-27 |
| GitHub Copilot CLI | Custom agents: `.github/agents/`, `~/.copilot/agents/`. Markdown files with the `.agent.md` extension. | `.github/hooks/*.json`, `~/.copilot/hooks/*.json`. `preToolUse` can deny. | [custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli), [hooks](https://docs.github.com/en/copilot/concepts/agents/hooks) | 2026-10-27 |
| GitHub Copilot in VS Code | `.github/agents/`, `~/.copilot/agents/` (`.agent.md`). Also `.claude/agents/` and `~/.claude/agents/` in Claude format. A custom agent can run as a sub-agent. | Preview. `.github/hooks/*.json`, `~/.copilot/hooks/`. `preToolUse` can deny. It also reads `.claude/settings.json`, but the docs say that tool names and data can be different. | [custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents), [hooks](https://code.visualstudio.com/docs/copilot/customization/hooks) | 2026-10-27 |
| Gemini CLI | `.gemini/agents/`, `~/.gemini/agents/`. Markdown with YAML frontmatter. | `.gemini/settings.json`, `~/.gemini/settings.json`. `BeforeTool` can deny. | [subagents](https://geminicli.com/docs/core/subagents/), [hooks](https://geminicli.com/docs/hooks/) | 2026-10-27 |
| Antigravity (CLI, IDE) | `.agents/agents/<name>.md`, `~/.gemini/config/agents/`. Markdown with YAML frontmatter. | CLI: `.agents/hooks.json`, `~/.gemini/config/hooks.json`. `PreToolUse` can deny. | [subagents](https://antigravity.google/docs/subagents), [hooks](https://antigravity.google/docs/hooks) | 2026-10-27 |
| Devin Desktop (was Windsurf), Devin Local agent | Preview. `.devin/agents/`, `.agents/agents/`, `~/.config/devin/agents/`. Markdown with YAML frontmatter. | `.devin/hooks.v1.json`. `PreToolUse` can block. It also loads hooks from `.claude/` by default. | [Devin Local](https://docs.devin.ai/desktop/devin-local), [subagents](https://docs.devin.ai/cli/subagents), [hooks](https://docs.devin.ai/cli/extensibility/hooks/overview) | 2026-10-27 |
| Cline | Only the built-in `spawn_agent` tool. Custom agent files: not documented. | Plugins in `.cline/plugins/`, `~/.cline/plugins/`. `beforeTool` can skip a tool call. Only in the Cline SDK, CLI and Kanban, not in the VS Code and JetBrains extensions. | [subagents](https://docs.cline.bot/features/subagents), [plugins](https://docs.cline.bot/customization/plugins), [SDK plugins](https://docs.cline.bot/sdk/plugins) | 2026-10-27 |
| OpenCode | `.opencode/agents/`, `~/.config/opencode/agents/`. Markdown with YAML frontmatter (`mode: subagent`). | Plugins in `.opencode/plugins/`, `~/.config/opencode/plugins/`. `tool.execute.before` can stop a tool call. | [agents](https://opencode.ai/docs/agents/), [plugins](https://opencode.ai/docs/plugins/) | 2026-10-27 |

Notes:

- Each hook system has its own file format. The qestack guard hook is in the Claude Code format. On other agents, use the CI guard (see [Without the hook](#without-the-hook)).
- Gemini CLI: for unpaid tier and Google One users, Antigravity CLI replaced Gemini CLI on 2026-06-18 ([notice](https://geminicli.com/docs/), [migration](https://antigravity.google/docs/cli/gcli-migration)).
- Devin Desktop: Windsurf became Devin Desktop on 2026-06-02. The old Cascade agent stayed available through July 2026. Cascade reads the same skill folders, and also `~/.codeium/windsurf/skills/`. Cascade has no sub-agents ([FAQ](https://docs.devin.ai/desktop/devin-desktop-faq), [Cascade skills](https://docs.devin.ai/desktop/cascade/skills)).
- GitHub Copilot cloud agent: the folders that it reads depend on the surface. Do not expect a user skill in a cloud session ([about agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)).
- `.agents/skills/` is the folder that most agents share. Claude Code, Cline and the Antigravity user level do not document it.

Status in 0.1: only Claude Code is tested. The other installs are planned for 0.2 with tested guides.

## Skills only (any agent that reads SKILL.md)

```bash
git clone https://github.com/quark-sri/qestack ~/qestack
cd ~/qestack
scripts/install-skills.sh --agent <name> --user               # for all your projects
scripts/install-skills.sh --agent <name> --project <repo>     # for one repository
```

| Option | Effect |
|---|---|
| `--agent <name>` | `claude`, `codex`, `cursor`, `copilot`, `gemini`, `antigravity`, `devin`, `opencode`, `cline`, or `all`. `all` is each agent except `claude`: Claude Code gets the skills from the plugin. An unknown name prints the list. |
| `--user` or `--project <repo>` | The user folder or the project folder of the agent, from the [skill folders](#skill-folders) table. Agents that share `.agents/skills/` get one install. |
| `--copy` | Copy the skills. The default is symbolic links. On Windows, use `--copy`: links need extra rights there. |
| `--library-only` | Install only the 39 library skills. Leave out the gated skills (`qestack`, `qe-*`). |

The script needs python3. It builds the [portable packages](#portable-packages) first and installs them, so the skills have only the spec fields. The links point to `dist/skills/` in the clone. After `git pull`, run the same command again to rebuild the packages. Codex documents that it follows linked skill folders. The other agents do not document this; if an agent does not find the linked skills, use `--copy`. The script does not change a folder that has the name of a qestack skill but is not from qestack.

The library skills need no engine. The gated skills (`qestack`, `qe-*`) also need the engine.

The old form `scripts/install-skills.sh <skills-folder>` still works. It links the source skills, with the Claude Code fields, into one folder.

The reviewer personas are agent files in `plugins/qestack/agents/`. Only the `test-review-panel` skill uses them. The script does not link them. If your agent cannot start the persona agents, the panel reads the persona texts and runs each persona as a separate reviewer. If the agent cannot start separate reviewers, the panel runs the personas one at a time in one session, and the report says that the review was not independent. The portable package of the panel has the persona texts in `references/personas/`. Use it when your agent has no access to the clone.

### Portable packages

The source skills have Claude Code fields, for example `argument-hint`. Some hosts reject these fields: claude.ai and the Skills API do. To get skills that have only the fields of the [Agent Skills spec](https://agentskills.io/specification), build the packages:

```bash
python3 scripts/build_skills.py                        # writes dist/
python3 scripts/validate_repo.py --spec dist/skills/*  # checks the output against the spec
```

| Output | Content |
|---|---|
| `dist/skills/<name>/` | Each skill, ready to copy into a skill folder |
| `dist/zips/<name>.zip` | One zip for each skill. The skill folder is the zip root. Use it for an upload. |
| `dist/qestack-skills.zip` | All 49 skills |
| `dist/qestack-qa-library.zip` | The 39 library skills only. They need no engine. |

Each package has `license`, a `metadata` map (author, version, source) and, for the gated skills, a `compatibility` line. The `test-review-panel` package also has the 8 persona texts in `references/personas/`, and the `qestack` package has the 4 workflow agent texts in `references/agents/`. The build copies them from `plugins/qestack/agents/`.

## Without sub-agents

Where an agent cannot start a separate sub-agent, run the role in a new session. Example for the judge: start a new session, give it the text of `plugins/qestack/agents/qe-test-judge.md`, and ask it to review the feature. For a review persona, give the new session the text of its file in `plugins/qestack/agents/`, for example `domain-oracle-reviewer.md`, or in `references/personas/` of the panel package. A new session has no memory of writing the tests, so the review is still independent. In the portable packages, the `qestack` skill has the 4 workflow agent texts in `references/agents/`. The `qestack` skill tells the agent to stop and ask for a new session for each role. It never does the writer, the judge or the fault seeder role in the same session.

## Without the hook

Run `qestack guard --feature <feature>` after each agent session, and in CI. The guard finds weakened, skipped and deleted tests against the base branch and the lock. Without the hook, nothing blocks a weakened test or an edit to a result file during the session. The CI guard is then the authority. `qestack init` also writes a short qestack section into `AGENTS.md`: the rules that the hook enforces in Claude Code, as instructions. Many agents read `AGENTS.md` at the start of each session, for example Codex, Cursor, GitHub Copilot, Gemini CLI, Devin and OpenCode ([agents.md](https://agents.md), checked 2026-10-29). Claude Code reads `CLAUDE.md`, and gets the hook instead. `qestack init` keeps the other text of an existing `AGENTS.md` and replaces only the qestack section. `--no-agents-md` turns this off. For a CI example, run `qestack show templates/ci-github-actions` and copy it to `.github/workflows/qestack.yml`.
