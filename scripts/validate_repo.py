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


# Skills
skills = sorted(p for pl in PLUGINS if (pl / "skills").exists() for p in (pl / "skills").iterdir() if p.is_dir())
names = [d.name for d in skills]
for n in sorted({n for n in names if names.count(n) > 1}):
    err(f"skill name '{n}' is used by more than one plugin")
for d in skills:
    f = d / "SKILL.md"
    if not f.exists():
        err(f"{d.relative_to(ROOT)}: SKILL.md missing")
        continue
    fm, body = frontmatter(f)
    if fm.get("name") != d.name:
        err(f"{f.relative_to(ROOT)}: name '{fm.get('name')}' does not match folder '{d.name}'")
    desc = fm.get("description", "")
    if not desc or len(desc) > 1024:
        err(f"{f.relative_to(ROOT)}: description missing or longer than 1024 characters")
    long_sentences(f, body)
    for ref in sorted((d / "references").glob("*.md")) if (d / "references").exists() else []:
        if ref.name not in body:
            err(f"{ref.relative_to(ROOT)}: not linked from SKILL.md")
        long_sentences(ref, ref.read_text(encoding="utf-8"))

# qe-skills rules: tool-neutral SKILL.md, routing parts in the description, shared context, existing related skills
TOOL_NAMES = re.compile(
    r"\b(maven|mvn|gradle|junit|testng|pytest|jest|vitest|mocha|cypress|playwright|selenium|selenide|pitest|stryker|"
    r"mutmut|docker|testcontainers|wiremock|mockito|assertj|rest assured|supertest|msw|k6|gatling|jmeter|locust|pact|"
    r"axe|lighthouse|bash|grep|glob tool|agent tool|webfetch)\b", re.I)
all_skill_names = set(names)
for d in skills:
    if d.parent.parent.name != "qe-skills":
        continue
    f = d / "SKILL.md"
    if not f.exists():
        continue
    fm, body = frontmatter(f)
    desc = fm.get("description", "")
    rp = f.relative_to(ROOT)
    if ": " in desc and not (desc.startswith('"') and desc.endswith('"')):
        err(f"{rp}: description has ': ' and must be one double-quoted line (valid YAML)")
    if '"' in desc.strip('"'):
        err(f"{rp}: description has a double quote inside; use single quotes for trigger phrases")
    for part in ("Use when:", "Not for:", "Related:"):
        if part not in desc:
            err(f"{rp}: description has no '{part}' part")
    rel_m = re.search(r"Related:\s*([^.]*)", desc)
    for n in (re.split(r",\s*", rel_m.group(1)) if rel_m else []):
        n = n.strip().strip('"')
        if n and n not in all_skill_names:
            err(f"{rp}: related skill '{n}' does not exist")
    for section in ("## Done when", "## Related skills"):
        if section not in body:
            err(f"{rp}: section '{section}' missing")
    if d.name != "qa-project-context" and "qa-project-context.md" not in body:
        err(f"{rp}: does not read .agents/qa-project-context.md")
    for m in TOOL_NAMES.finditer(re.sub(r"\[[^\]]*\]\(references/[^)]*\)", "", body + " " + desc)):
        err(f"{rp}: names the tool '{m.group(0)}'; put tool details in references/")

# Agents
agents =sorted(f for pl in PLUGINS for f in (pl / "agents").glob("*.md"))
for f in agents:
    fm, body = frontmatter(f)
    if fm.get("name") != f.stem:
        err(f"{f.relative_to(ROOT)}: name '{fm.get('name')}' does not match file name")
    for k in ("description", "tools"):
        if not fm.get(k):
            err(f"{f.relative_to(ROOT)}: '{k}' missing")
    long_sentences(f, body)

# qe-skills personas: persona files in the test-review-panel skill, run by the test-reviewer agent.
# Only test-review-panel may use them, so that the other skills stay self-contained.
QE = ROOT / "plugins" / "qe-skills"
PANEL = QE / "skills" / "test-review-panel"
persona_files = sorted((PANEL / "references" / "personas").glob("*.md"))
personas = {p.stem for p in persona_files}
panel_body = (PANEL / "SKILL.md").read_text(encoding="utf-8") if (PANEL / "SKILL.md").exists() else ""
for p in persona_files:
    fm, body = frontmatter(p)
    rp = p.relative_to(ROOT)
    if fm.get("name") != p.stem:
        err(f"{rp}: name '{fm.get('name')}' does not match file name")
    for k in ("title", "description"):
        if not fm.get(k):
            err(f"{rp}: '{k}' missing")
    if fm.get("mode") not in ("read-only", "changes-code"):
        err(f"{rp}: mode must be 'read-only' or 'changes-code'")
    if fm.get("runs-commands") not in ("yes", "no"):
        err(f"{rp}: runs-commands must be 'yes' or 'no'")
    sections = ["## Scope", "## Evidence rule", "## Output", "## Limits"]
    if fm.get("mode") == "changes-code":
        sections.append("## Safety rules")
    for section in sections:
        if section not in body:
            err(f"{rp}: section '{section}' missing")
    for m in TOOL_NAMES.finditer(body + " " + fm.get("description", "")):
        err(f"{rp}: names the tool '{m.group(0)}'")
    if f"references/personas/{p.name}" not in panel_body:
        err(f"{rp}: not linked from the test-review-panel skill")
    long_sentences(p, body)
MODE_AGENTS = {"read-only": "test-reviewer", "changes-code": "test-saboteur"}
for mode in sorted({frontmatter(p)[0].get("mode") for p in persona_files} & MODE_AGENTS.keys()):
    a = QE / "agents" / f"{MODE_AGENTS[mode]}.md"
    if not a.exists():
        err(f"{a.relative_to(ROOT)}: missing; the '{mode}' personas need it")
    elif mode == "read-only" and re.search(r"\b(Edit|Write|NotebookEdit)\b", frontmatter(a)[0].get("tools", "")):
        err(f"{a.relative_to(ROOT)}: runs read-only personas and must have no edit tools")
for a in (QE / "agents").glob("*.md"):
    for m in TOOL_NAMES.finditer(frontmatter(a)[1]):
        err(f"{a.relative_to(ROOT)}: names the tool '{m.group(0)}'")
panel_names = sorted(personas | {"test-reviewer", "test-saboteur"})
persona_rx = re.compile(r"`(" + "|".join(map(re.escape, panel_names)) + r")`")
for d in skills:
    f = d / "SKILL.md"
    if d.parent.parent != QE or d == PANEL or not f.exists():
        continue
    for m in persona_rx.finditer(f.read_text(encoding="utf-8")):
        err(f"{f.relative_to(ROOT)}: names '{m.group(1)}'; only test-review-panel may use the personas")

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
