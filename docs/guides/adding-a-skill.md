# Add or change a skill or an agent

The skills and agents follow the Claude standards for skills and subagents. `scripts/validate_repo.py` checks each rule that has a "checked" mark. Run it before each commit.

Sources: [Claude Code skills](https://code.claude.com/docs/en/skills), [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) and [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Skill name

- At most 64 characters: lowercase letters, digits and hyphens. No "anthropic" or "claude". (checked)
- The folder name and the `name` field are the same. (checked)
- Gated workflow skills start with `qe-`. Library skills do not. (checked: the validator uses the name to choose the rules)

## Skill description

Claude Code keeps the descriptions of all skills in one listing. The listing gets about 1% of the context window: about 10,000 tokens for a 1M context and 2,000 tokens for a 200k context. When it is full, Claude Code drops the descriptions of the skills that are used least, and Claude can no longer match those skills to a request. The 15,000-character limit (about 3,750 tokens) fits a 1M context. A 200k context is too small for all descriptions of this plugin. So keep each description short, and use `skillOverrides` with `"name-only"` in the settings for the skills that a team does not use.

| Rule | Checked |
|---|---|
| One double-quoted line. Single quotes for trigger phrases. No `<` or `>` | yes |
| Starts with a verb in the third person: "Writes", "Finds", "Tests" | yes |
| What the skill does first, then when to use it: "Use when the user says '...'" | yes |
| Library skills: one "Not for ... (use <skill>)" part; the named skill exists | yes |
| At most 350 characters. All skill descriptions together at most 15,000 characters | yes |
| Plain words that users type, for example 'flaky test' or 'load test' | review |
| No list of related skills. The "Related skills" section of the body has them | review |

Template:

```yaml
description: "Finds the root cause of a flaky test: <two to five key methods>. Use when the user says '<trigger>', '<trigger>' or '<trigger>'. Not for <neighbor job> (use <other-skill>)."
```

## Skill frontmatter

- Use only the fields that Claude Code knows. Claude Code ignores an unknown field without an error, so a typo has no effect. (checked)
- The plugin uses `name`, `description` and `argument-hint`.
- Outside Claude Code (an upload to claude.ai or the Skills API), only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` are allowed. Remove `argument-hint` before such an upload.

## Skill body and references

- The `SKILL.md` body has less than 500 lines. Put tool details and long catalogs in `references/`. (checked)
- `SKILL.md` links each reference file. A reference file does not link another markdown file: references stay one level deep. (checked)
- A reference file with more than 100 lines starts with a `## Contents` section. (checked)
- Library skills: no tool names in `SKILL.md`, the sections "Done when" and "Related skills", and a step that reads `.agents/qa-project-context.md`. (checked)
- Put the most important instructions near the top. After compaction, Claude Code keeps only the start of a skill.
- Use forward slashes in paths. Do not write instructions that depend on a date.

## Agents

- `name`, `description` and `tools` are required. The name is the file name, with no `:`. (checked)
- Use only known fields. Plugin agents ignore `hooks`, `mcpServers`, `permissionMode` and `initialPrompt`, so do not use them. (checked)
- Each tool in `tools` is a known Claude Code tool. (checked)
- The description is at most 400 characters and says when to start the agent. Personas start with "Read-only qestack review persona." Workflow agents start with "qestack workflow agent.". (checked: length)
- Persona rules: no edit tools, the shared "Reviewer rules" section, and a row in `test-review-panel`. (checked)

## After the change

1. Run `python3 scripts/build_llms_txt.py` to update `llms.txt`.
2. Run `python3 scripts/validate_repo.py`.
3. Add a routing eval case in `plugins/qestack/evals/routing/`: a realistic request, a `skill-fired` grader and, if there is a close neighbor, a `<neighbor>-not-fired` grader. Copy an existing case. Run it with `claude plugin eval . --case <case> --ablation none --no-publish` from `plugins/qestack` (see `docs/library-session-test.md`).
