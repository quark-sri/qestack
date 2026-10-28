#!/usr/bin/env python3
"""Build portable skill packages for all agents that read SKILL.md (Agent Skills spec, agentskills.io).

Standard library only. Run:
    python3 scripts/build_skills.py [--out <folder>]     (default: dist/)
Then check the output against the spec:
    python3 scripts/validate_repo.py --spec dist/skills/*

Output:
    skills/<name>/              each skill, with only the spec frontmatter fields and a metadata map
    skills/test-review-panel/references/personas/<name>.md
                                the 8 reviewer persona texts, for hosts that cannot start the plugin agents
    zips/<name>.zip             one zip for each skill; the skill folder is the zip root
    qestack-skills.zip          all skills
    qestack-qa-library.zip      the library skills only (no engine needed)
The source keeps the Claude Code fields (for example argument-hint); the build removes them.
The persona texts have one source: the agent files in plugins/qestack/agents/. The build copies them unchanged.
"""
import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "qestack"
PANEL = "test-review-panel"
SOURCE = "https://github.com/quark-sri/qestack"
# Keep the same list as SPEC_SKILL_KEYS in validate_repo.py. metadata is written by the build.
SPEC_KEYS = ("name", "description", "license", "compatibility", "allowed-tools")
BUNDLES = {"qestack-skills.zip": lambda name: True, "qestack-qa-library.zip": lambda name: not gated(name)}
ZIP_TIME = (1980, 1, 1, 0, 0, 0)  # a fixed time, so the same source gives the same zip


def gated(name):
    return name == "qestack" or name.startswith("qe-")


def personas():
    """The review persona agent files: all agents except the workflow agents (qe-*)."""
    return sorted(f for f in (PLUGIN / "agents").glob("*.md") if not f.stem.startswith("qe-"))


def portable(text, version):
    """SKILL.md text with only the spec fields, in the source order, and a metadata map at the end."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit("SKILL.md has no frontmatter")
    lines = m.group(1).splitlines()
    if any(line[:1] in " \t" for line in lines):
        raise SystemExit("SKILL.md frontmatter has a nested value; the build supports only one line for each field")
    keep = [line for line in lines if line.split(":", 1)[0].strip() in SPEC_KEYS]
    keep += ["metadata:", "  author: quark-sri", f'  version: "{version}"', f"  source: {SOURCE}"]
    return "---\n" + "\n".join(keep) + "\n---\n" + text[m.end():]


def write_zip(path, folders, base):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in folders:
            for f in sorted(p for p in folder.rglob("*") if p.is_file()):
                info = zipfile.ZipInfo(f.relative_to(base).as_posix(), ZIP_TIME)
                info.external_attr = 0o644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, f.read_bytes())


def main():
    ap = argparse.ArgumentParser(description="Build portable skill packages.")
    ap.add_argument("--out", type=Path, default=ROOT / "dist", help="output folder (default: dist/)")
    out = ap.parse_args().out.resolve()
    version = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())["version"]

    for old in [out / "skills", out / "zips", *(out / b for b in BUNDLES)]:  # only what this script writes
        if old.is_dir():
            shutil.rmtree(old)
        elif old.exists():
            old.unlink()
    (out / "zips").mkdir(parents=True)

    skills = sorted(d for d in (PLUGIN / "skills").iterdir() if (d / "SKILL.md").exists())
    for src in skills:
        dst = out / "skills" / src.name
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        (dst / "SKILL.md").write_text(portable((src / "SKILL.md").read_text(encoding="utf-8"), version),
                                      encoding="utf-8")
        if src.name == PANEL:
            (dst / "references" / "personas").mkdir(parents=True)
            for f in personas():
                shutil.copyfile(f, dst / "references" / "personas" / f.name)
        write_zip(out / "zips" / f"{src.name}.zip", [dst], out / "skills")
    for bundle, wanted in BUNDLES.items():
        write_zip(out / bundle, [out / "skills" / d.name for d in skills if wanted(d.name)], out / "skills")

    library = sum(not gated(d.name) for d in skills)
    print(f"{out}: {len(skills)} skills ({library} library, {len(skills) - library} gated), "
          f"{len(skills)} zips, {len(BUNDLES)} bundles, {len(personas())} persona texts in {PANEL}")


if __name__ == "__main__":
    main()
