#!/usr/bin/env python3
"""Validate the qestack repository: skills, agents, manifests, data files, versions and links.

Standard library only. Exit code 1 on errors. Long sentences are warnings (writing style).
Run: python3 scripts/validate_repo.py
"""
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "qestack"
PLUGINS = sorted(p for p in (ROOT / "plugins").iterdir() if (p / ".claude-plugin" / "plugin.json").exists())
DATA = ROOT / "engine" / "src" / "qestack" / "data"
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{path.relative_to(ROOT)}: no YAML frontmatter")
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def long_sentences(path, body, limit=30):
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    for line in body.splitlines():
        if line.lstrip().startswith("|"):
            continue
        for sent in re.split(r"(?<=[.!?])\s+", line):
            words = re.findall(r"[A-Za-z][\w'-]*", sent)
            if len(words) > limit:
                warnings.append(f"{path.relative_to(ROOT)}: sentence with {len(words)} words: {sent[:70]}...")


# Claude skill and subagent standards (Claude Code skills and subagents docs, Agent Skills best practices):
# - name: at most 64 characters, lowercase letters, digits and hyphens, no reserved words
# - description: third person, what the skill does and when to use it, key use case first, no XML tags.
#   Claude Code keeps all skill descriptions in one listing of about 1% of the context window, so keep them short.
# - SKILL.md body under 500 lines; references one level deep; a "Contents" section in references over 100 lines
# - only known frontmatter keys: Claude Code ignores unknown keys without an error, so a typo goes unnoticed
# - plugin subagents ignore hooks, mcpServers, permissionMode and initialPrompt
SKILL_KEYS = {"name", "description", "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
              "user-invocable", "allowed-tools", "disallowed-tools", "model", "effort", "context", "agent",
              "background", "hooks", "paths", "shell", "metadata", "license", "compatibility"}
AGENT_KEYS = {"name", "description", "tools", "disallowedTools", "model", "maxTurns", "autoCompactWindow", "skills",
              "memory", "background", "omitClaudeMd", "effort", "isolation", "color", "experimental"}
AGENT_KEYS_IGNORED_IN_PLUGINS = {"hooks", "mcpServers", "permissionMode", "initialPrompt"}
TOOLS = {"Read", "Grep", "Glob", "Bash", "Edit", "Write", "MultiEdit", "NotebookEdit", "WebFetch", "WebSearch",
         "Agent", "Skill"}
NAME_RX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_DESC_MAX = 350          # each skill; the documented hard limit is 1024
# All skills of the plugin, about 3,750 tokens. The listing budget is 1% of the context window: this fits a 1M
# context with room for other skills. A 200k context (2,000 tokens) is smaller; there Claude Code drops the
# descriptions of the skills that are used least.
SKILL_DESC_TOTAL_MAX = 15000
AGENT_DESC_MAX = 400
BODY_MAX_LINES = 500


def check_description(rp, desc, limit):
    if not desc:
        err(f"{rp}: description missing")
        return ""
    if ": " in desc and not (desc.startswith('"') and desc.endswith('"')):
        err(f"{rp}: description has ': ' and must be one double-quoted line (valid YAML)")
    text = desc[1:-1] if desc.startswith('"') and desc.endswith('"') else desc
    if '"' in text:
        err(f"{rp}: description has a double quote inside; use single quotes for trigger phrases")
    if "<" in text or ">" in text:
        err(f"{rp}: description has '<' or '>'; XML tags are not allowed")
    if len(text) > limit:
        err(f"{rp}: description has {len(text)} characters; keep it at {limit} or less")
    return text


# Skills
skills = sorted(p for pl in PLUGINS if (pl / "skills").exists() for p in (pl / "skills").iterdir() if p.is_dir())
names = [d.name for d in skills]
all_skill_names = set(names)
for n in sorted({n for n in names if names.count(n) > 1}):
    err(f"skill name '{n}' is used by more than one plugin")
desc_total = 0
for d in skills:
    f = d / "SKILL.md"
    if not f.exists():
        err(f"{d.relative_to(ROOT)}: SKILL.md missing")
        continue
    rp = f.relative_to(ROOT)
    fm, body = frontmatter(f)
    if fm.get("name") != d.name:
        err(f"{rp}: name '{fm.get('name')}' does not match folder '{d.name}'")
    if not NAME_RX.match(d.name) or len(d.name) > 64 or re.search(r"anthropic|claude", d.name):
        err(f"{rp}: name must be at most 64 lowercase letters, digits and hyphens, without 'anthropic' or 'claude'")
    for k in sorted(set(fm) - SKILL_KEYS):
        err(f"{rp}: unknown frontmatter key '{k}'; Claude Code ignores it")
    desc = check_description(rp, fm.get("description", ""), SKILL_DESC_MAX)
    desc_total += len(desc)
    if desc and not re.match(r"[A-Z][a-z]+(?<!s)s\b", desc):  # "Writes", not "Write" or "Process"
        err(f"{rp}: description must start with a verb in the third person, for example 'Writes' or 'Finds'")
    if desc and "Use " not in desc:
        err(f"{rp}: description does not say when to use the skill ('Use when ...')")
    for n in re.findall(r"\(use ([a-z0-9-]+)\)", desc):
        if n not in all_skill_names:
            err(f"{rp}: description names the skill '{n}', which does not exist")
    if len(body.splitlines()) > BODY_MAX_LINES:
        err(f"{rp}: body has more than {BODY_MAX_LINES} lines; move details to references/")
    long_sentences(f, body)
    for ref in sorted((d / "references").glob("*.md")) if (d / "references").exists() else []:
        text = ref.read_text(encoding="utf-8")
        if ref.name not in body:
            err(f"{ref.relative_to(ROOT)}: not linked from SKILL.md")
        if re.search(r"\]\((?!https?://)[^)]*\.md\b", text):
            err(f"{ref.relative_to(ROOT)}: links another markdown file; keep references one level deep from SKILL.md")
        if len(text.splitlines()) > 100 and not re.search(r"^## Contents", text, re.M):
            err(f"{ref.relative_to(ROOT)}: more than 100 lines and no '## Contents' section at the top")
        long_sentences(ref, text)
if desc_total > SKILL_DESC_TOTAL_MAX:
    err(f"skill descriptions have {desc_total} characters in total; keep them at {SKILL_DESC_TOTAL_MAX} or less")

# Two skill groups in one plugin, by name: the gated workflow (`qestack`, `qe-*`) needs the engine.
# All other skills are the library: tool-neutral SKILL.md, "Use when" and "Not for" in the description,
# shared context, existing related skills.
def gated(name):
    return name == "qestack" or name.startswith("qe-")


TOOL_NAMES = re.compile(
    r"\b(maven|mvn|gradle|junit|testng|pytest|jest|vitest|mocha|cypress|playwright|selenium|selenide|pitest|stryker|"
    r"mutmut|docker|testcontainers|wiremock|mockito|assertj|rest assured|supertest|msw|k6|gatling|jmeter|locust|pact|"
    r"axe|lighthouse|bash|grep|glob tool|agent tool|webfetch)\b", re.I)
for d in skills:
    if gated(d.name):
        continue
    f = d / "SKILL.md"
    if not f.exists():
        continue
    fm, body = frontmatter(f)
    desc = fm.get("description", "").strip('"')
    rp = f.relative_to(ROOT)
    for part in ("Use when", "Not for"):
        if part not in desc:
            err(f"{rp}: description has no '{part}' part")
    for section in ("## Done when", "## Related skills"):
        if section not in body:
            err(f"{rp}: section '{section}' missing")
    rel = body.split("## Related skills", 1)[1] if "## Related skills" in body else ""
    for n in re.findall(r"^- `([a-z0-9-]+)`", rel, re.M):
        if n not in all_skill_names:
            err(f"{rp}: related skill '{n}' does not exist")
    if d.name != "qa-project-context" and "qa-project-context.md" not in body:
        err(f"{rp}: does not read .agents/qa-project-context.md")
    for m in TOOL_NAMES.finditer(re.sub(r"\[[^\]]*\]\(references/[^)]*\)", "", body + " " + desc)):
        err(f"{rp}: names the tool '{m.group(0)}'; put tool details in references/")

# Agents
agents = sorted(f for pl in PLUGINS for f in (pl / "agents").glob("*.md"))
for f in agents:
    rp = f.relative_to(ROOT)
    fm, body = frontmatter(f)
    if fm.get("name") != f.stem:
        err(f"{rp}: name '{fm.get('name')}' does not match file name")
    if ":" in fm.get("name", "") or fm.get("name", "").startswith("-"):
        err(f"{rp}: name must not contain ':' or start with '-'; Claude Code skips the agent")
    for k in ("description", "tools"):
        if not fm.get(k):
            err(f"{rp}: '{k}' missing")
    for k in sorted(set(fm) & AGENT_KEYS_IGNORED_IN_PLUGINS):
        err(f"{rp}: '{k}' is ignored for plugin subagents")
    for k in sorted(set(fm) - AGENT_KEYS - AGENT_KEYS_IGNORED_IN_PLUGINS):
        err(f"{rp}: unknown frontmatter key '{k}'; Claude Code ignores it")
    for t in [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]:
        if not t.startswith("mcp__") and t.split("(", 1)[0] not in TOOLS:  # also "Bash(git *)" and MCP tools
            err(f"{rp}: unknown tool '{t}'")
    check_description(rp, fm.get("description", ""), AGENT_DESC_MAX)
    long_sentences(f, body)

# Two agent classes, by name: workflow agents (`qe-*`) change files through the engine. All other agents are
# review personas: one agent per persona, no edit tools, one shared "Reviewer rules" section.
# Only test-review-panel may use the personas, so that the other skills stay self-contained.
PANEL = PLUGIN / "skills" / "test-review-panel"
persona_agents = [f for f in agents if not f.stem.startswith("qe-")]
personas = {p.stem for p in persona_agents}
panel_body = (PANEL / "SKILL.md").read_text(encoding="utf-8") if (PANEL / "SKILL.md").exists() else ""
EDIT_TOOLS = re.compile(r"\b(Edit|Write|MultiEdit|NotebookEdit)\b")
rules = {}
for p in persona_agents:
    fm, body = frontmatter(p)
    rp = p.relative_to(ROOT)
    if EDIT_TOOLS.search(fm.get("tools", "")):
        err(f"{rp}: a persona must not have edit tools; personas report, the caller changes code")
    for section in ("## Reviewer rules", "## Scope", "## Evidence rule", "## Output", "## Limits"):
        if section not in body:
            err(f"{rp}: section '{section}' missing")
    m = re.search(r"## Reviewer rules\n(.*?)\n## ", body, re.S)
    if m:
        rules[p.stem] = m.group(1)
    for m in TOOL_NAMES.finditer(body + " " + fm.get("description", "")):
        err(f"{rp}: names the tool '{m.group(0)}'")
    if f"`{p.stem}`" not in panel_body:
        err(f"{rp}: not in the test-review-panel skill")
if len(set(rules.values())) > 1:
    first = sorted(rules)[0]
    for n in sorted(rules):
        if rules[n] != rules[first]:
            err(f"plugins/qestack/agents/{n}.md: 'Reviewer rules' differs from {first}.md; keep it the same in all personas")
for token in ("qa-reviews/", "panel-report.md", "findings.json", "references/findings-format.md"):
    if persona_agents and token not in panel_body:
        err(f"{(PANEL / 'SKILL.md').relative_to(ROOT)}: does not name '{token}' (review folder and findings format)")
persona_rx = re.compile(r"`(" + "|".join(map(re.escape, sorted(personas))) + r")`") if personas else None
for d in skills:
    f = d / "SKILL.md"
    if d == PANEL or not f.exists() or not persona_rx:
        continue
    for m in persona_rx.finditer(f.read_text(encoding="utf-8")):
        err(f"{f.relative_to(ROOT)}: names the persona '{m.group(1)}'; only test-review-panel may use the personas")

# llms.txt lists each skill and each agent, for AI agents and skill registries
llms = ROOT / "llms.txt"
llms_text = llms.read_text(encoding="utf-8") if llms.exists() else ""
for n in [d.name for d in skills] + [f.stem for f in agents]:
    if f"[{n}](" not in llms_text:
        err(f"llms.txt: '{n}' missing; run python3 scripts/build_llms_txt.py")

# JSON files
for f in [ROOT / ".claude-plugin" / "marketplace.json", *(pl / ".claude-plugin" / "plugin.json" for pl in PLUGINS),
          PLUGIN / "hooks" / "hooks.json", *DATA.rglob("*.json")]:
    try:
        json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{f.relative_to(ROOT)}: invalid JSON: {e}")

# TOML files and regexes
def check_regex(path, key, value):
    try:
        re.compile(value)
    except re.error as e:
        err(f"{path.relative_to(ROOT)}: bad regex in {key}: {e}")


def walk(path, node, key=""):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(path, v, f"{key}.{k}" if key else k)
    elif isinstance(node, list):
        for v in node:
            if isinstance(v, str) and ("regex" in key or "pattern" in key):
                check_regex(path, key, v)
    elif isinstance(node, str) and ("regex" in key or "patterns" in key):
        check_regex(path, key, node)


for f in sorted(DATA.rglob("*.toml")):
    try:
        walk(f, tomllib.loads(f.read_text(encoding="utf-8")))
    except tomllib.TOMLDecodeError as e:
        err(f"{f.relative_to(ROOT)}: invalid TOML: {e}")

# Each stack and ruleset has a guide
for kind in ("stacks", "rulesets"):
    for t in (DATA / kind).glob("*.toml"):
        if not t.with_suffix(".md").exists():
            err(f"{t.relative_to(ROOT)}: guide {t.with_suffix('.md').name} missing")
for r in (DATA / "rulesets").glob("*.md"):
    if "Seeded faults for this layer" not in r.read_text(encoding="utf-8"):
        err(f"{r.relative_to(ROOT)}: section 'Seeded faults for this layer' missing")

# Counts in the public descriptions agree with the files (they drift when a skill or persona is added)
n_library = sum(1 for d in skills if not gated(d.name))
count_rx = re.compile(r"(\d+) Quality Engineering skills and (\d+) reviewer personas")
for f, text in [("plugins/qestack/.claude-plugin/plugin.json", (PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")),
                (".claude-plugin/marketplace.json", (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")),
                ("README.md", (ROOT / "README.md").read_text(encoding="utf-8")),
                ("llms.txt", llms_text)]:
    found = count_rx.findall(text)
    if not found:
        err(f"{f}: no '<n> Quality Engineering skills and <m> reviewer personas' text")
    for a, b in found:
        if (int(a), int(b)) != (n_library, len(personas)):
            err(f"{f}: says {a} skills and {b} personas; the plugin has {n_library} library skills and {len(personas)} personas")

# The guard hook of the plugin and the hook that 'qestack init --hook' installs are the same
plugin_hook = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
init_hook = json.loads((DATA / "templates" / "claude-settings.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
if plugin_hook != init_hook:
    err("plugins/qestack/hooks/hooks.json and engine/src/qestack/data/templates/claude-settings.json: "
        "the PreToolUse hooks differ; keep them the same")

# Versions agree
init = (ROOT / "engine" / "src" / "qestack" / "__init__.py").read_text()
engine_v = re.search(r'__version__ = "([^"]+)"', init).group(1)
market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
versions = {"engine": engine_v}
for pl in PLUGINS:
    versions[f"plugin {pl.name}"] = json.loads((pl / ".claude-plugin" / "plugin.json").read_text())["version"]
for e in market["plugins"]:
    versions[f"marketplace {e['name']}"] = e.get("version")
    if not (ROOT / e["source"]).resolve().is_dir():
        err(f"marketplace: source {e['source']} not found")
if len(set(versions.values())) != 1:
    err("versions differ: " + ", ".join(f"{k} {v}" for k, v in versions.items()))

# Relative links in markdown
for f in ROOT.rglob("*.md"):
    if ".git" in f.parts:
        continue
    for m in re.finditer(r"\]\((?!https?://|mailto:|#)([^)#\s]+)(?:#[^)]*)?\)", f.read_text(encoding="utf-8")):
        target = (f.parent / m.group(1)).resolve()
        if not target.exists():
            err(f"{f.relative_to(ROOT)}: broken link {m.group(1)}")

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"\nplugins: {len(PLUGINS)}, skills: {len(skills)}, agents: {len(agents)}, "
      f"errors: {len(errors)}, warnings: {len(warnings)}")
sys.exit(1 if errors else 0)
