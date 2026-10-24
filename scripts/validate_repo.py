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
skills = sorted(p for p in (PLUGIN / "skills").iterdir() if p.is_dir())
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

# Agents
for f in sorted((PLUGIN / "agents").glob("*.md")):
    fm, body = frontmatter(f)
    if fm.get("name") != f.stem:
        err(f"{f.relative_to(ROOT)}: name '{fm.get('name')}' does not match file name")
    for k in ("description", "tools"):
        if not fm.get(k):
            err(f"{f.relative_to(ROOT)}: '{k}' missing")
    long_sentences(f, body)

# JSON files
for f in [ROOT / ".claude-plugin" / "marketplace.json", PLUGIN / ".claude-plugin" / "plugin.json",
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
plugin_v = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())["version"]
market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
market_v = market["plugins"][0]["version"]
if len({engine_v, plugin_v, market_v}) != 1:
    err(f"versions differ: engine {engine_v}, plugin {plugin_v}, marketplace {market_v}")

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
print(f"\nskills: {len(skills)}, agents: {len(list((PLUGIN / 'agents').glob('*.md')))}, "
      f"errors: {len(errors)}, warnings: {len(warnings)}")
sys.exit(1 if errors else 0)
