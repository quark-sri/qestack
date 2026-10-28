#!/usr/bin/env python3
"""Write llms.txt: one index of the qestack plugin for AI agents, crawlers and skill registries.

Standard library only. Run after you add, rename or describe a skill or an agent:
    python3 scripts/build_llms_txt.py
The validator checks that each skill and each agent is in llms.txt.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "qestack"
BASE = "https://github.com/quark-sri/qestack/blob/main/"


def describe(path):
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    fm = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    desc = fm["description"].strip().strip('"')
    # Drop a short leading label ("qestack workflow agent.", "Read-only qestack review persona.").
    # Then keep the first clause: the text before the first ": ", " - " or the end of the first sentence.
    desc = re.sub(r"^(Read-only )?qestack [^.]{0,40}\.\s+", "", desc)
    return re.split(r": | - |\.\s", desc)[0].strip().rstrip(".")


def gated(name):
    return name == "qestack" or name.startswith("qe-")


def row(path, name):
    return f"- [{name}]({BASE}{path.relative_to(ROOT).as_posix()}): {describe(path)}"


skills = sorted(d for d in (PLUGIN / "skills").iterdir() if (d / "SKILL.md").exists())
agents = sorted((PLUGIN / "agents").glob("*.md"))
lines = [
    "# qestack",
    "",
    "> qestack: QA and test automation skills, agents and quality gates for AI coding agents. One Claude Code plugin "
    "with a QA library (39 Quality Engineering skills and 8 reviewer personas for any stack, no engine needed) and a "
    "gated workflow with an engine that proves AI-written tests catch bugs (spec-first test design, red-before-green, "
    "test locks, hidden faults, mutation score, independent judge).",
    "",
    "Install in Claude Code: `/plugin marketplace add quark-sri/qestack`, then `/plugin install qestack@qestack`. "
    "Other agents that read SKILL.md: `scripts/install-skills.sh --agent <name> --user` (see docs/other-agents.md).",
    "",
    "## Docs",
    "",
    f"- [README]({BASE}README.md): what qestack does, install, gates and limits",
    f"- [Why qestack]({BASE}docs/why-qestack.md): the problem with AI-written tests and the metrics",
    f"- [Architecture]({BASE}docs/architecture.md): engine, plugin, hook and project folder",
    f"- [Other agents]({BASE}docs/other-agents.md): use the skills with Codex, Cursor and Copilot",
    "",
    "## QA library skills (no engine needed)",
    "",
    *(row(d / "SKILL.md", d.name) for d in skills if not gated(d.name)),
    "",
    "## Gated workflow skills (need the qestack engine)",
    "",
    *(row(d / "SKILL.md", d.name) for d in skills if gated(d.name)),
    "",
    "## Review personas (read-only agents)",
    "",
    *(row(f, f.stem) for f in agents if not f.stem.startswith("qe-")),
    "",
    "## Workflow agents (gated workflow)",
    "",
    *(row(f, f.stem) for f in agents if f.stem.startswith("qe-")),
    "",
]
(ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"llms.txt: {len(skills)} skills, {len(agents)} agents")
