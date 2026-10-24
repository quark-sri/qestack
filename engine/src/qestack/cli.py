#!/usr/bin/env python3
"""
qestack - AI test quality gates.

Measures the quality of (AI-written) tests with objective gates:
lint (hollow / no-assertion / trivial / shallow / skipped / smells),
requirement traceability, red-before-green, flakiness, mutation score,
seeded-fault detection, anti-gaming guard, test locks, scoring,
feedback for the next improvement iteration, and judge calibration.

Requirements: Python 3.11 or later (uses tomllib). No third-party packages.
Language support comes from stacks (Java/JUnit 5, .NET, ...). Test-area rules come
from rulesets (API, database, Kafka, UI). Project settings live in .qestack/project.toml.

Run "qestack --help" or "qestack <command> --help".

Copyright 2026 The qestack authors. Licensed under the Apache License, Version 2.0.
"""
from __future__ import annotations

import argparse
import fnmatch
import glob as globmod
import hashlib
import json
import os
import random
import re
import shlex
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        sys.stderr.write("qestack needs Python 3.11+ (tomllib) or the 'tomli' package.\n")
        sys.exit(2)

from qestack import __version__ as TOOL_VERSION  # noqa: E402

# --------------------------------------------------------------------------------------
# Paths and configuration
# --------------------------------------------------------------------------------------


def _git_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except FileNotFoundError:
        pass
    return Path.cwd()


BUILD_FILES = ("pom.xml", "build.gradle", "build.gradle.kts", "package.json", "pyproject.toml")


def _find_root() -> Path:
    """The project root: QESTACK_ROOT, else the nearest folder up to the git root with .qestack/,
    else the current folder if it is a sub-project with its own build file (monorepo), else the git root."""
    if os.environ.get("QESTACK_ROOT"):
        return Path(os.environ["QESTACK_ROOT"])
    top, cwd = _git_root().resolve(), Path.cwd().resolve()
    for d in (cwd, *cwd.parents):
        if (d / ".qestack" / "project.toml").is_file():
            return d
        if d == top:
            break
    if cwd != top and cwd.is_relative_to(top) and (any((cwd / b).exists() for b in BUILD_FILES) or any(cwd.glob("*.csproj"))):
        return cwd
    return top


ROOT = _find_root()
QE_DIR = ROOT / ".qestack"
DATA_DIR = Path(__file__).resolve().parent / "data"
PKG_DIR = Path(__file__).resolve().parent


def deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif isinstance(v, list) and k.startswith("extra_"):
            out[k[6:]] = list(out.get(k[6:]) or []) + v
        else:
            out[k] = v
    return out


def _load_toml(p: Path) -> dict:
    with open(p, "rb") as fh:
        return tomllib.load(fh)


class Cfg(dict):
    """dict with dotted access: cfg.get_path('gates.mutation_min', 0.75)."""

    def get_path(self, dotted: str, default=None):
        cur = self
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur


def find_layer(kind: str, name: str, ext: str) -> Path | None:
    """A stack or ruleset file: the project folder first, then the bundled data."""
    for base in (QE_DIR / kind, DATA_DIR / kind):
        p = base / f"{name}.{ext}"
        if p.exists():
            return p
    return None


def project_settings() -> dict:
    p = QE_DIR / "project.toml"
    return _load_toml(p) if p.exists() else {}


def load_config() -> Cfg:
    cfg = _load_toml(DATA_DIR / "defaults.toml")
    proj = project_settings()
    pr = proj.get("project", {})
    stack = pr.get("stack")
    rulesets = pr.get("rulesets", [])
    if stack:
        sp = find_layer("stacks", stack, "toml")
        if sp:
            cfg = deep_merge(cfg, _load_toml(sp))
        elif not find_layer("stacks", stack, "md"):
            warn(f"Stack '{stack}' not found. Run 'qestack show stacks' to list the stacks.")
    for rs in rulesets:
        rp = find_layer("rulesets", rs, "toml")
        if rp:
            cfg = deep_merge(cfg, _load_toml(rp))
        elif not find_layer("rulesets", rs, "md"):
            warn(f"Ruleset '{rs}' not found. Run 'qestack show rulesets' to list the rulesets.")
    cfg = deep_merge(cfg, proj)
    return Cfg(cfg)


def warn(msg: str):
    sys.stderr.write(f"[qestack] WARNING: {msg}\n")


def info(msg: str):
    sys.stderr.write(f"[qestack] {msg}\n")


def die(msg: str, code: int = 2):
    sys.stderr.write(f"[qestack] ERROR: {msg}\n")
    sys.exit(code)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(p) -> str:
    p = Path(p)
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def write_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(p: Path, default=None):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        warn(f"Invalid JSON in {rel(p)}: {e}")
        return default


# --------------------------------------------------------------------------------------
# Glob helpers ("**" aware, relative POSIX paths)
# --------------------------------------------------------------------------------------

_GLOB_CACHE: dict = {}


def glob_to_regex(pattern: str) -> re.Pattern:
    if pattern in _GLOB_CACHE:
        return _GLOB_CACHE[pattern]
    i, out = 0, ""
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif c == "*":
            out += "[^/]*"
            i += 1
        elif c == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(c)
            i += 1
    rx = re.compile("^" + out + "$")
    _GLOB_CACHE[pattern] = rx
    return rx


def matches_any(path: str, patterns) -> bool:
    return any(glob_to_regex(p).match(path) for p in patterns or [])


def list_repo_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if out.returncode == 0:
            files = [f for f in out.stdout.splitlines() if f]
            return [f for f in files if (ROOT / f).exists()]
    except FileNotFoundError:
        pass
    files = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "node_modules", "target", "build", "bin", "obj")]
        for f in fn:
            files.append(rel(Path(dp) / f))
    return files


def find_files(cfg: Cfg, include_key: str) -> list[str]:
    inc = cfg.get_path(f"paths.{include_key}", [])
    exc = cfg.get_path("paths.exclude_globs", [])
    return sorted(f for f in list_repo_files() if matches_any(f, inc) and not matches_any(f, exc))


def is_protected(cfg: Cfg, path: str) -> bool:
    return matches_any(path, cfg.get_path("paths.protected", []))


# --------------------------------------------------------------------------------------
# Git helpers
# --------------------------------------------------------------------------------------


def git(*args, check=False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=check)


def git_head() -> str:
    r = git("rev-parse", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else ""


def ref_exists(ref: str) -> bool:
    return bool(ref) and git("rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode == 0


def resolve_base(cfg: Cfg, arg: str | None) -> str | None:
    for cand in [arg, os.environ.get("QESTACK_BASE_REF"), cfg.get_path("git.base_ref"), "origin/main", "main", "origin/master", "master"]:
        if cand and ref_exists(cand):
            mb = git("merge-base", cand, "HEAD")
            return mb.stdout.strip() if mb.returncode == 0 and mb.stdout.strip() else cand
    return None


def changed_files(base: str | None) -> list[str]:
    files = set()
    if base:
        # --relative: paths from ROOT (not from the git top), and only files below ROOT
        r = git("diff", "--name-only", "--relative", base)
        files.update(f for f in r.stdout.splitlines() if f)
    r = git("ls-files", "--others", "--exclude-standard")
    files.update(f for f in r.stdout.splitlines() if f)
    return sorted(files)


def git_show(ref: str, path: str) -> str | None:
    r = git("show", f"{ref}:./{path}")  # "./": the path is from ROOT, which can be below the git top
    return r.stdout if r.returncode == 0 else None


# --------------------------------------------------------------------------------------
# Feature resolution (speckit: specs/<NNN-name>/)
# --------------------------------------------------------------------------------------


class Feature:
    def __init__(self, cfg: Cfg, name: str, path: Path):
        self.name = name
        self.dir = path
        m = re.match(r"^(\d+)", name)
        self.num = m.group(1) if m else name
        fmt = cfg.get_path("requirements.feature_tag_format", "feature-{num}")
        self.tag = fmt.replace("{num}", self.num).replace("{name}", name)
        self.runs = ROOT / cfg.get_path("paths.runs_dir", ".qestack/runs") / name
        self.locks = ROOT / cfg.get_path("paths.locks_dir", ".qestack/locks")
        self.spec = path / "spec.md"
        self.plan = path / "plan.md"
        self.test_plan = path / "test-plan.md"

    def to_dict(self):
        return {
            "name": self.name, "dir": rel(self.dir), "num": self.num, "feature_tag": self.tag,
            "runs_dir": rel(self.runs), "spec": rel(self.spec), "plan": rel(self.plan),
            "test_plan": rel(self.test_plan), "lock_file": rel(self.locks / f"{self.name}.json"),
        }


FEATURE_NAME_RX = re.compile(r"^[\w.-]+$")


def resolve_feature(cfg: Cfg, arg: str | None, strict: bool = False) -> Feature:
    f = _resolve_feature(cfg, arg, strict)
    if not FEATURE_NAME_RX.match(f.name):
        die(f"Feature name '{f.name}' has characters that are not allowed. Use letters, digits, '-', '_' and '.'.")
    return f


def _resolve_feature(cfg: Cfg, arg: str | None, strict: bool) -> Feature:
    specs = ROOT / cfg.get_path("paths.specs_dir", "specs")
    cands = []
    if arg and arg != "auto":
        cands.append(arg)
    for env in ("QESTACK_FEATURE", "SPECIFY_FEATURE", "GITHUB_HEAD_REF"):
        if os.environ.get(env):
            cands.append(os.environ[env])
    br = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if br and br != "HEAD":
        cands.append(br)
    dirs = sorted([d for d in specs.iterdir() if d.is_dir()]) if specs.exists() else []
    for c in cands:
        c = c.rstrip("/")
        name = Path(c).name
        if (specs / name).is_dir():
            return Feature(cfg, name, specs / name)
        if Path(c).is_dir() and (Path(c) / "spec.md").exists():
            return Feature(cfg, Path(c).name, Path(c).resolve())
        m = re.match(r"^(\d+)", name)
        if m:
            num = m.group(1)
            hits = [d for d in dirs if re.match(rf"^0*{int(num)}-", d.name) or d.name == num]
            if len(hits) == 1:
                return Feature(cfg, hits[0].name, hits[0])
    if arg and arg != "auto":
        die(f"Feature '{arg}' not found under {rel(specs)}/")
    if dirs and strict:
        die("This command changes files. Give the feature with --feature (the branch name does not match a feature).")
    if dirs:
        newest = max(dirs, key=lambda d: d.stat().st_mtime)
        warn(f"Feature not given and not found from branch; using newest: {newest.name}")
        return Feature(cfg, newest.name, newest)
    die(f"No feature directories under {rel(specs)}/. Pass --feature.")


# --------------------------------------------------------------------------------------
# Source scanning (pattern based, language neutral; regexes come from the stack)
# --------------------------------------------------------------------------------------


def mask_source(text: str, style: str):
    """Return (nocomment, masked).
    nocomment: comments blanked (strings kept).
    masked: comments and string/char literal contents blanked. Newlines and offsets kept."""
    n = len(text)
    nc = list(text)
    mk = list(text)

    def blank(arr, a, b):
        for k in range(max(a, 0), min(b, n)):
            if arr[k] != "\n":
                arr[k] = " "

    i = 0
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            blank(nc, i, j)
            blank(mk, i, j)
            i = j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(nc, i, j)
            blank(mk, i, j)
            i = j
            continue
        if text.startswith('"""', i):
            j = text.find('"""', i + 3)
            j = n if j < 0 else j + 3
            blank(mk, i + 3, j - 3)
            i = j
            continue
        if style == "csharp" and (text.startswith('@"', i) or text.startswith('$@"', i) or text.startswith('@$"', i)):
            start = text.index('"', i) + 1
            j = start
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            blank(mk, start, j)
            i = j + 1
            continue
        if c == '"' or c == "'":
            q = c
            j = i + 1
            while j < n and text[j] != q and text[j] != "\n":
                if text[j] == "\\":
                    j += 2
                    continue
                j += 1
            blank(mk, i + 1, j)
            i = j + 1
            continue
        i += 1
    return "".join(nc), "".join(mk)


def match_close(masked: str, i: int, open_c: str, close_c: str) -> int:
    depth = 0
    for j in range(i, len(masked)):
        ch = masked[j]
        if ch == open_c:
            depth += 1
        elif ch == close_c:
            depth -= 1
            if depth == 0:
                return j
    return -1


def member_start(masked: str, pos: int) -> int:
    """Walk back from pos to the end of the previous member ({ } ; at paren depth 0)."""
    depth = 0
    j = pos - 1
    while j >= 0:
        ch = masked[j]
        if ch in ")]":
            depth += 1
        elif ch in "([":
            if depth == 0:
                return j + 1
            depth -= 1
        elif ch in "{};" and depth == 0:
            return j + 1
        j -= 1
    return 0


def statement_end(masked: str, start: int, limit: int) -> int:
    depth = 0
    j = start
    while j < limit:
        ch = masked[j]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                return j
            depth -= 1
        elif ch == ";" and depth == 0:
            return j
        j += 1
    return limit


def norm_stmt(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*([.()\[\],])\s*", r"\1", s)
    return s


JAVA_KEYWORDS = {"if", "for", "while", "switch", "catch", "synchronized", "return", "new", "else", "try", "do",
                 "foreach", "using", "lock", "fixed", "when", "nameof", "typeof", "sizeof", "default"}


class Lang:
    def __init__(self, cfg: Cfg):
        L = cfg.get("language", {})
        self.style = L.get("string_style", "java")
        self.marker = re.compile(L.get("test_marker_regex") or r"(?!x)x")
        self.skip = re.compile(L.get("skip_regex") or r"(?!x)x")
        self.class_rx = re.compile(L.get("class_regex", r"\b(?:class|record|struct)\s+(\w+)"))
        self.display = re.compile(L.get("display_name_regex") or r"(?!x)x")
        self.assertion_rx = [re.compile(r) for r in L.get("assertion_regexes", []) + L.get("custom_assertion_regexes", [])]
        self.trivial_rx = [re.compile(r) for r in L.get("trivial_statement_regexes", [])]
        self.shallow_rx = [re.compile(r) for r in L.get("shallow_statement_regexes", [])]
        self.tag_rx = [re.compile(r) for r in cfg.get_path("tags.tag_value_regex", [])]
        self.smells = {k: re.compile(v, re.M) for k, v in cfg.get_path("smells.patterns", {}).items()}
        self.todo = re.compile(cfg.get_path("smells.todo_regex", r"\b(?:TODO|FIXME|XXX)\b"))
        req = cfg.get("requirements", {})
        self.id_rx = re.compile(r"^(?:%s)$" % req.get("id_regex", r"(?:FR|NFR|SC|AC|EC|BR)-\d{2,4}"))
        self.scn_rx = re.compile(r"^(?:%s)$" % req.get("scenario_id_regex", r"US\d+-AS\d+"))
        self.categories = {c.lower() for c in cfg.get_path("tags.category_values", [])}
        fmt = req.get("feature_tag_format", "feature-{num}")
        self.feature_rx = re.compile("^" + re.escape(fmt).replace(re.escape("{num}"), r"(\d+)").replace(re.escape("{name}"), r"(.+)") + "$")


def classify_tags(lang: Lang, tags):
    ids, cats, feats, other = [], [], [], []
    for t in tags:
        tt = t.strip()
        if lang.id_rx.match(tt) or lang.scn_rx.match(tt):
            ids.append(tt)
        elif tt.lower() in lang.categories:
            cats.append(tt.lower())
        elif lang.feature_rx.match(tt):
            feats.append(tt)
        else:
            other.append(tt)
    return ids, cats, feats, other


def extract_tags(lang: Lang, text: str):
    out = []
    for rx in lang.tag_rx:
        out.extend(m.group(1) for m in rx.finditer(text))
    return out


def find_assertions(lang: Lang, nc: str, mk: str, a: int, b: int, helpers):
    """Return list of normalized assertion statements in nc[a:b]."""
    starts = set()
    for rx in lang.assertion_rx:
        for m in rx.finditer(mk, a, b):
            starts.add(m.start())
    for h in helpers:
        for m in re.finditer(r"(?<![\w.])" + re.escape(h) + r"\s*\(", mk[a:b]):
            starts.add(a + m.start())
    stmts = []
    last_end = -1
    for s in sorted(starts):
        if s < last_end:  # nested match inside the previous statement (e.g. assertAll(...))
            continue
        e = statement_end(mk, s, b)
        stmts.append(norm_stmt(nc[s:e]))
        last_end = e
    return stmts


def classify_statements(lang: Lang, stmts):
    trivial = shallow = 0
    for s in stmts:
        if any(r.search(s) for r in lang.trivial_rx):
            trivial += 1
        elif any(r.search(s) for r in lang.shallow_rx):
            shallow += 1
    return trivial, shallow


def find_helpers(lang: Lang, nc: str, mk: str, test_spans):
    """Names of non-test methods in this file whose body contains an assertion."""
    helpers = set()
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\([^;{}()]*(?:\([^;{}()]*\)[^;{}()]*)*\)\s*(?:throws\s+[\w.,\s]+)?\{", mk):
        name = m.group(1)
        if name in JAVA_KEYWORDS:
            continue
        if any(s <= m.start() <= e for s, e in test_spans):
            continue
        brace = mk.find("{", m.end() - 1)
        end = match_close(mk, brace, "{", "}")
        if end < 0:
            continue
        body = mk[brace + 1:end]
        if any(r.search(body) for r in lang.assertion_rx):
            helpers.add(name)
    return helpers


def parse_tests(lang: Lang, text: str, path: str):
    """Return list of test-method dicts in one source file."""
    nc, mk = mask_source(text, lang.style)
    line_of = lambda pos: text.count("\n", 0, pos) + 1  # noqa: E731

    classes = []
    for m in lang.class_rx.finditer(mk):
        brace = mk.find("{", m.end())
        semi = mk.find(";", m.end())
        if brace < 0 or (0 <= semi < brace):
            continue
        end = match_close(mk, brace, "{", "}")
        if end < 0:
            continue
        region_start = member_start(mk, m.start())
        region = nc[region_start:m.start()]
        classes.append({
            "name": m.group(1), "start": brace, "end": end,
            "tags": extract_tags(lang, region), "skipped": bool(lang.skip.search(region)),
        })

    tests = []
    raw = []
    for m in lang.marker.finditer(mk):
        pos = m.end()
        n = len(mk)
        # skip the rest of the attribute / further annotations
        while pos < n:
            while pos < n and mk[pos].isspace():
                pos += 1
            if pos >= n:
                break
            ch = mk[pos]
            if ch == "(":
                e = match_close(mk, pos, "(", ")")
                pos = e + 1 if e > 0 else pos + 1
            elif ch == "@":
                pos += 1
                while pos < n and (mk[pos].isalnum() or mk[pos] in "._"):
                    pos += 1
            elif ch == "[":
                e = match_close(mk, pos, "[", "]")
                pos = e + 1 if e > 0 else pos + 1
            elif ch in "],":
                # inside a C# attribute list: jump to its closing bracket
                depth = 0
                while pos < n:
                    c2 = mk[pos]
                    if c2 == "(":
                        depth += 1
                    elif c2 == ")":
                        depth -= 1
                    elif c2 == "]" and depth <= 0:
                        pos += 1
                        break
                    pos += 1
            else:
                break
        p = mk.find("(", pos)
        if p < 0:
            continue
        nm = re.search(r"([A-Za-z_]\w*)\s*(?:<[^<>]*>)?\s*$", mk[pos:p])
        if not nm:
            continue
        name = nm.group(1)
        q = match_close(mk, p, "(", ")")
        if q < 0:
            continue
        brace = mk.find("{", q + 1)
        semi = mk.find(";", q + 1)
        arrow = mk.find("=>", q + 1)
        expr_body = False
        if arrow >= 0 and (brace < 0 or arrow < brace) and (semi < 0 or arrow < semi):
            a, b = arrow + 2, (semi if semi >= 0 else n)
            expr_body = True
        elif brace >= 0 and (semi < 0 or brace < semi):
            end = match_close(mk, brace, "{", "}")
            if end < 0:
                continue
            a, b = brace + 1, end
        else:
            continue
        region_start = member_start(mk, m.start())
        raw.append((m, name, region_start, p, a, b, expr_body))

    spans = [(r[2], r[5]) for r in raw]
    helpers = find_helpers(lang, nc, mk, spans)

    seen = set()
    for (m, name, region_start, p, a, b, expr_body) in raw:
        if (name, a) in seen:
            continue
        seen.add((name, a))
        region = nc[region_start:p]
        encl = [c for c in classes if c["start"] < m.start() < c["end"]]
        encl.sort(key=lambda c: c["start"])
        cls = encl[-1]["name"] if encl else Path(path).stem
        tags = list(extract_tags(lang, region))
        cls_skipped = False
        for c in encl:
            tags = c["tags"] + tags
            cls_skipped = cls_skipped or c["skipped"]
        ids, cats, feats, other = classify_tags(lang, tags)
        body_nc = nc[a:b]
        body_code = re.sub(r"[\s;]", "", mk[a:b])
        hollow = (not expr_body) and body_code == ""
        stmts = find_assertions(lang, nc, mk, a, b, helpers)
        trivial, shallow = classify_statements(lang, stmts)
        strong = len(stmts) - trivial - shallow
        if hollow:
            cls_name = "HOLLOW"
        elif not stmts:
            cls_name = "NO_ASSERTION"
        elif strong > 0:
            cls_name = "OK"
        elif shallow > 0:
            cls_name = "SHALLOW"
        else:
            cls_name = "TRIVIAL"
        smells = [k for k, rx in lang.smells.items() if rx.search(body_nc)]
        dn = lang.display.search(region)
        tests.append({
            "key": f"{path}::{cls}.{name}",
            "file": path,
            "line": line_of(p),
            "class": cls,
            "method": name,
            "display_name": dn.group(1) if dn else "",
            "tags": tags,
            "ids": sorted(set(ids)),
            "categories": sorted(set(cats)),
            "features": sorted(set(feats)),
            "skipped": bool(lang.skip.search(region)) or cls_skipped,
            "todo": bool(lang.todo.search(text[a:b])),
            "classification": cls_name,
            "assertions": len(stmts),
            "strong": strong,
            "trivial": trivial,
            "shallow": shallow,
            "assertion_statements": stmts,
            "smells": smells,
            "body_hash": hashlib.sha256((norm_stmt(region) + "|" + norm_stmt(body_nc)).encode()).hexdigest()[:16],
        })
    return tests


def scan_all_tests(cfg: Cfg, files=None):
    lang = Lang(cfg)
    files = files if files is not None else find_files(cfg, "test_globs")
    out = []
    for f in files:
        try:
            text = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.extend(parse_tests(lang, text, f))
    return out


def scope_tests(tests, feature: Feature | None):
    if feature is None:
        return tests
    return [t for t in tests if feature.tag in t["features"]]


# --------------------------------------------------------------------------------------
# lint
# --------------------------------------------------------------------------------------


def lint_summary(tests):
    s = {
        "total": len(tests),
        "hollow": sum(t["classification"] == "HOLLOW" for t in tests),
        "no_assertion": sum(t["classification"] == "NO_ASSERTION" for t in tests),
        "trivial": sum(t["classification"] == "TRIVIAL" for t in tests),
        "shallow": sum(t["classification"] == "SHALLOW" for t in tests),
        "ok": sum(t["classification"] == "OK" for t in tests),
        "skipped": sum(t["skipped"] for t in tests),
        "todo": sum(t["todo"] for t in tests),
        "untraced": sum(not t["ids"] for t in tests),
        "uncategorized": sum(not t["categories"] for t in tests),
        "tests_with_smells": sum(bool(t["smells"]) for t in tests),
        "smells_by_type": {},
    }
    for t in tests:
        for sm in t["smells"]:
            s["smells_by_type"][sm] = s["smells_by_type"].get(sm, 0) + 1
    n = max(1, len(tests))
    s["smell_rate"] = round(s["tests_with_smells"] / n, 4)
    s["weak_rate"] = round((s["hollow"] + s["no_assertion"] + s["trivial"] + s["shallow"]) / n, 4)
    return s


def cmd_lint(args, cfg):
    feature = None if args.all else resolve_feature(cfg, args.feature)
    files = args.files or None
    tests = scan_all_tests(cfg, files)
    scoped = tests if (args.all or files) else scope_tests(tests, feature)
    if feature and not scoped:
        warn(f"No tests carry the feature tag '{feature.tag}'. Tag the test classes, or use --all.")
    summary = lint_summary(scoped)
    findings = []
    for t in scoped:
        problems = []
        if t["classification"] != "OK":
            problems.append(t["classification"])
        if t["skipped"]:
            problems.append("SKIPPED")
        if t["todo"]:
            problems.append("TODO")
        if not t["ids"]:
            problems.append("UNTRACED")
        if not t["categories"]:
            problems.append("UNCATEGORIZED")
        problems += [f"SMELL:{s}" for s in t["smells"]]
        if problems:
            findings.append({"key": t["key"], "file": t["file"], "line": t["line"], "problems": problems})
    result = {"tool": "qestack.lint", "version": TOOL_VERSION, "created": now_iso(),
              "feature": feature.name if feature else None, "scope": "all" if args.all else (feature.tag if feature else "files"),
              "summary": summary, "findings": findings, "tests": scoped}
    if feature:
        write_json(feature.runs / "lint.json", result)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"lint: {summary['total']} tests | hollow={summary['hollow']} no_assertion={summary['no_assertion']} "
              f"trivial={summary['trivial']} shallow={summary['shallow']} skipped={summary['skipped']} "
              f"todo={summary['todo']} untraced={summary['untraced']} smells={summary['tests_with_smells']}")
        for f in findings[: args.max]:
            print(f"  {f['file']}:{f['line']}  {f['key'].split('::')[-1]}  {', '.join(f['problems'])}")
        if len(findings) > args.max:
            print(f"  ... {len(findings) - args.max} more (see lint.json)")
    G = cfg.get("gates", {})
    hard = (summary["hollow"] + summary["no_assertion"] + summary["skipped"]
            + (summary["trivial"] > G.get("trivial_max", 0)) + (summary["shallow"] > G.get("shallow_max", 0)))
    return 1 if hard else 0


# --------------------------------------------------------------------------------------
# trace
# --------------------------------------------------------------------------------------


def parse_spec(cfg: Cfg, path: Path):
    reqs = {}
    if not path.exists():
        return reqs
    text = path.read_text(encoding="utf-8", errors="replace")
    idrx = cfg.get_path("requirements.id_regex", r"(?:FR|NFR|SC|AC|EC|BR)-\d{2,4}")
    def_rx = re.compile(r"^\s*(?:[-*+]|\d+\.|\|)?\s*(?:\*\*|__)?\s*(" + idrx + r")\s*(?:\*\*|__)?\s*[:|.–—-]\s*(.*)$")
    for line in text.splitlines():
        m = def_rx.match(line)
        if m and m.group(1) not in reqs:
            reqs[m.group(1)] = {"id": m.group(1), "text": m.group(2).strip().strip("|").strip()[:200], "source": "spec"}
    if not reqs:
        for m in re.finditer(idrx, text):
            reqs.setdefault(m.group(0), {"id": m.group(0), "text": "", "source": "spec"})
    if cfg.get_path("requirements.derive_scenario_ids", True):
        story, in_acc = None, False
        for line in text.splitlines():
            h = re.match(r"^#{1,6}\s+User Story\s+(\d+)", line, re.I)
            if h:
                story, in_acc = h.group(1), False
                continue
            if re.match(r"^#{1,6}\s", line) or line.strip() == "---":
                if not h:
                    story, in_acc = (story if line.strip() != "---" else None), False
                continue
            if story and re.search(r"acceptance scenarios", line, re.I):
                in_acc = True
                continue
            if story and in_acc:
                mm = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
                if mm:
                    sid = f"US{story}-AS{mm.group(1)}"
                    reqs[sid] = {"id": sid, "text": re.sub(r"\*\*", "", mm.group(2)).strip()[:200], "source": "spec-scenario"}
    for r in reqs.values():
        r["needs_clarification"] = "NEEDS CLARIFICATION" in r["text"].upper()
    return reqs


def parse_test_plan(cfg: Cfg, path: Path, lang: Lang):
    """Parse the traceability table in test-plan.md. Returns {id: {"categories": [...], "excluded": bool, "text": str}}."""
    plan = {}
    if not path.exists():
        return plan
    idrx = cfg.get_path("requirements.id_regex", r"(?:FR|NFR|SC|AC|EC|BR)-\d{2,4}")
    scn = cfg.get_path("requirements.scenario_id_regex", r"US\d+-AS\d+")
    any_id = re.compile(r"\b(?:%s|%s)\b" % (idrx, scn))
    header = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip().startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if any("categor" in c for c in low) and any(("req" in c) or ("id" == c) for c in low):
            header = low
            continue
        if header is None or set("".join(cells)) <= set("-: "):
            continue
        m = any_id.search(cells[0]) if cells else None
        if not m:
            continue
        rid = m.group(0)
        cat_idx = next((i for i, h in enumerate(header) if "categor" in h), None)
        cats_cell = cells[cat_idx].lower() if cat_idx is not None and cat_idx < len(cells) else ""
        excluded = bool(re.search(r"\bn/?a\b|out[- ]of[- ]scope|not testable", cats_cell))
        cats = sorted({c for c in re.split(r"[^a-z]+", cats_cell) if c in lang.categories})
        text = cells[1] if len(cells) > 1 else ""
        plan[rid] = {"categories": cats, "excluded": excluded, "text": text[:200], "row": cells}
    return plan


def required_ids(cfg: Cfg, spec_reqs, plan):
    prefixes = cfg.get_path("requirements.required_prefixes", ["FR", "US", "EC", "AC", "BR"])
    allreq = dict(spec_reqs)
    for rid, p in plan.items():
        allreq.setdefault(rid, {"id": rid, "text": p.get("text", ""), "source": "test-plan"})
    req, excluded = {}, {}
    for rid, r in allreq.items():
        pref = re.match(r"^([A-Z]+)", rid).group(1)
        if pref not in prefixes:
            continue
        if plan.get(rid, {}).get("excluded"):
            excluded[rid] = r
        else:
            req[rid] = r
    return req, excluded, allreq


def depth_rule(cfg: Cfg, rid: str, plan):
    if rid in plan and plan[rid]["categories"]:
        return {"all": plan[rid]["categories"], "any": [], "source": "test-plan"}
    rules = cfg.get_path("requirements.depth_rules", {})
    pref = re.match(r"^([A-Z]+)", rid).group(1)
    r = rules.get(pref, rules.get("default", {"all": [], "any": []}))
    return {"all": r.get("all", []), "any": r.get("any", []), "source": "default"}


def counts_for_coverage(t) -> bool:
    return not t["skipped"] and t["classification"] == "OK"


def compute_trace(cfg: Cfg, feature: Feature, tests):
    lang = Lang(cfg)
    spec_reqs = parse_spec(cfg, feature.spec)
    plan = parse_test_plan(cfg, feature.test_plan, lang)
    req, excluded, allreq = required_ids(cfg, spec_reqs, plan)
    cov = {rid: {"tests": [], "categories": set()} for rid in allreq}
    unknown = {}
    orphans = []
    for t in tests:
        if not t["ids"]:
            orphans.append(t["key"])
        for rid in t["ids"]:
            if rid not in cov:
                unknown.setdefault(rid, []).append(t["key"])
                continue
            if counts_for_coverage(t):
                cov[rid]["tests"].append(t["key"])
                cov[rid]["categories"].update(t["categories"])
    rows = []
    covered = depth_ok_n = 0
    for rid, r in req.items():
        c = cov.get(rid, {"tests": [], "categories": set()})
        rule = depth_rule(cfg, rid, plan)
        missing_all = [x for x in rule["all"] if x not in c["categories"]]
        any_ok = (not rule["any"]) or bool(set(rule["any"]) & c["categories"])
        is_cov = bool(c["tests"])
        d_ok = is_cov and not missing_all and any_ok
        covered += is_cov
        depth_ok_n += d_ok
        rows.append({
            "id": rid, "text": r.get("text", ""), "source": r.get("source"),
            "needs_clarification": r.get("needs_clarification", False),
            "tests": c["tests"], "categories_found": sorted(c["categories"]),
            "required_all": rule["all"], "required_any": rule["any"], "rule_source": rule["source"],
            "missing_categories": missing_all + ([] if any_ok else ["one of: " + "/".join(rule["any"])]),
            "covered": is_cov, "depth_ok": d_ok,
            "in_test_plan": rid in plan,
        })
    n = max(1, len(req))
    return {
        "tool": "qestack.trace", "version": TOOL_VERSION, "created": now_iso(), "feature": feature.name,
        "spec_found": feature.spec.exists(), "test_plan_found": feature.test_plan.exists(),
        "summary": {
            "required_total": len(req), "covered": covered, "coverage": round(covered / n, 4) if req else 0.0,
            "depth_ok": depth_ok_n, "depth_ratio": round(depth_ok_n / n, 4) if req else 0.0,
            "tests_in_scope": len(tests), "orphans": len(orphans),
            "orphan_rate": round(len(orphans) / max(1, len(tests)), 4), "unknown_ids": len(unknown),
            "plan_coverage": round(sum(1 for rid in req if rid in plan) / n, 4) if req else 0.0,
            "excluded_by_plan": len(excluded),
        },
        "requirements": rows,
        "excluded_by_plan": [{"id": k, "text": v.get("text", ""), "plan_row": plan.get(k, {}).get("row")} for k, v in excluded.items()],
        "orphans": orphans,
        "unknown_ids": unknown,
    }


def cmd_trace(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    tests = scope_tests(scan_all_tests(cfg), feature)
    result = compute_trace(cfg, feature, tests)
    write_json(feature.runs / ("trace-plan.json" if args.plan_only else "trace.json"), result)
    s = result["summary"]
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    if not result["spec_found"]:
        warn(f"spec.md not found: {rel(feature.spec)}")
    if args.plan_only:
        missing = [r["id"] for r in result["requirements"] if not r["in_test_plan"]]
        print(f"trace(plan): {s['required_total']} required IDs | in test plan: {s['required_total'] - len(missing)} "
              f"({s['plan_coverage']:.0%}) | excluded by plan: {s['excluded_by_plan']}")
        for rid in missing:
            print(f"  MISSING IN PLAN: {rid}")
        return 1 if missing or not result["test_plan_found"] else 0
    print(f"trace: required={s['required_total']} covered={s['covered']} ({s['coverage']:.0%}) "
          f"depth_ok={s['depth_ok']} ({s['depth_ratio']:.0%}) orphans={s['orphans']} unknown_ids={s['unknown_ids']}")
    for r in result["requirements"]:
        if not r["covered"]:
            print(f"  UNCOVERED  {r['id']}: {r['text'][:90]}")
        elif not r["depth_ok"]:
            print(f"  SHALLOW    {r['id']}: missing {', '.join(r['missing_categories'])}")
    for rid, keys in result["unknown_ids"].items():
        print(f"  UNKNOWN ID {rid} used by {len(keys)} test(s)")
    return 0 if s["coverage"] >= cfg.get_path("gates.trace_coverage_min", 1.0) else 1


# --------------------------------------------------------------------------------------
# Running tests and parsing JUnit XML
# --------------------------------------------------------------------------------------


PRE_QUOTED = {"changed_files"}


def fill(cmd: str, mapping: dict) -> str:
    for k, v in mapping.items():
        v = str(v)
        cmd = cmd.replace("{" + k + "}", v if k in PRE_QUOTED or v == "" else shlex.quote(v))
    return cmd


def run_cmd(cmd: str, cfg: Cfg, label: str):
    if not cmd:
        die(f"No command configured for '{label}'. Set it in project.toml [commands].")
    timeout = cfg.get_path("commands.timeout_seconds", 3600)
    info(f"run ({label}): {cmd}")
    t0 = time.time()
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "") + (r.stderr or "")
        code = r.returncode
    except subprocess.TimeoutExpired as e:
        out = f"TIMEOUT after {timeout}s\n" + str(e.stdout or "")
        code = 124
    return code, out[-6000:], round(time.time() - t0, 1)


def clean_reports(cfg: Cfg):
    if not cfg.get_path("reports.clean_before_run", True):
        return
    for pat in cfg.get_path("reports.junit_globs", []):
        for f in globmod.glob(str(ROOT / pat), recursive=True):
            if f.endswith(".xml"):
                try:
                    os.remove(f)
                except OSError:
                    pass


def norm_case_name(name: str) -> str:
    n = re.sub(r"\(.*$", "", name or "")
    n = re.sub(r"\[.*$", "", n)
    n = n.strip()
    return n.split(".")[-1] if "." in n and " " not in n else n


def parse_junit(cfg: Cfg, since: float | None = None):
    """Return {(simple_class, name): status} with status in passed/failed/error/skipped."""
    res = {}
    rank = {"passed": 0, "passed_on_rerun": 1, "skipped": 2, "failed": 3, "error": 4}
    for pat in cfg.get_path("reports.junit_globs", []):
        for f in globmod.glob(str(ROOT / pat), recursive=True):
            if since and os.path.getmtime(f) < since - 2:
                continue
            try:
                tree = ET.parse(f)
            except ET.ParseError:
                continue
            for tc in tree.getroot().iter("testcase"):
                cls = (tc.get("classname") or "").split(".")[-1].split("$")[-1].split("+")[-1]
                name = norm_case_name(tc.get("name", ""))
                if tc.find("failure") is not None:
                    st = "failed"
                elif tc.find("error") is not None:
                    st = "error"
                elif tc.find("skipped") is not None:
                    st = "skipped"
                elif any(tc.find(x) is not None for x in ("flakyFailure", "flakyError", "rerunFailure", "rerunError")):
                    st = "passed_on_rerun"  # Surefire rerunFailingTestsCount hid a failure
                else:
                    st = "passed"
                k = (cls, name)
                if k not in res or rank[st] > rank[res[k]]:
                    res[k] = st
    return res


def status_for(test, results, raw: bool = False):
    st = None
    for k in ((test["class"], test["method"]), (test["class"], test.get("display_name", ""))):
        if k in results:
            st = results[k]
            break
    else:
        hits = [v for (c, n), v in results.items() if n == test["method"]]  # method name only (unique match)
        if len(hits) == 1:
            st = hits[0]
    if st == "passed_on_rerun" and not raw:
        return "passed"
    return st


# --------------------------------------------------------------------------------------
# red (red-before-green)
# --------------------------------------------------------------------------------------


def cmd_red(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    tests = [t for t in scope_tests(scan_all_tests(cfg), feature) if not t["skipped"]]
    if not tests:
        die(f"No tests with tag '{feature.tag}' found.")
    t0 = time.time()
    code, out = 0, ""
    if not args.skip_run:
        clean_reports(cfg)
        code, out, _ = run_cmd(fill(cfg.get_path("commands.test_feature", ""), {"feature_tag": feature.tag, "feature": feature.name}), cfg, "test_feature")
    results = parse_junit(cfg, None if args.skip_run else t0)
    exempt = set(read_json(feature.locks / f"{feature.name}.red-exempt.json", []) or [])
    errors_count = cfg.get_path("gates.red_counts_errors", True)
    ok, viol, notrun, exempted, by_error, error_only = [], [], [], [], [], []
    for t in tests:
        st = status_for(t, results)
        if t["key"] in exempt:
            exempted.append(t["key"])
        elif st == "failed":
            ok.append(t["key"])
        elif st == "error":
            by_error.append(t["key"])
            (ok if errors_count else error_only).append(t["key"])
        elif st == "passed":
            viol.append(t["key"])
        else:
            notrun.append(t["key"])
    status = "OK"
    if not results:
        status = "INVALID"
        warn("No test results found. The build or test compilation probably failed. Check the output below.")
        print(out[-3000:])
    considered = len(ok) + len(viol) + len(error_only)
    result = {"tool": "qestack.red", "created": now_iso(), "feature": feature.name, "git_head": git_head(),
              "status": status, "exit_code": code,
              "summary": {"tests": len(tests), "red": len(ok), "red_by_assertion": len(ok) - (len(by_error) if errors_count else 0),
                          "red_by_error": len(by_error), "green_before_impl": len(viol), "not_run": len(notrun),
                          "exempt": len(exempted), "rate": round(len(ok) / considered, 4) if considered else 0.0},
              "red": ok, "red_by_error": by_error, "error_only": error_only, "violations": viol, "not_run": notrun,
              "exempt": exempted}
    write_json(feature.runs / "red.json", result)
    s = result["summary"]
    print(f"red: {s['red']}/{s['tests']} failed before implementation (rate {s['rate']:.0%}); "
          f"by assertion={s['red_by_assertion']} by error={s['red_by_error']} "
          f"passed-too-early={s['green_before_impl']} not_run={s['not_run']} exempt={s['exempt']} status={status}")
    if by_error and errors_count:
        print("  NOTE: a test that fails with an error (for example a stub that throws) proves less than an assertion failure. "
              "Set gates.red_counts_errors = false to require assertion failures.")
    for k in error_only:
        print(f"  FAILS ONLY WITH AN ERROR: {k}")
    for k in viol:
        print(f"  PASSES BEFORE IMPLEMENTATION: {k}")
    for k in notrun[:20]:
        print(f"  NOT RUN: {k}")
    return 0 if status == "OK" and not viol and not notrun and not error_only else 1


# --------------------------------------------------------------------------------------
# flaky
# --------------------------------------------------------------------------------------


def cmd_flaky(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    tests = [t for t in scope_tests(scan_all_tests(cfg), feature) if not t["skipped"]]
    runs = args.runs or cfg.get_path("gates.flaky_runs", 5)
    cmd = cfg.get_path("commands.test_feature_random", "") or cfg.get_path("commands.test_feature", "")
    hist = {t["key"]: [] for t in tests}
    invalid_runs = 0
    seeds = []
    for i in range(runs):
        clean_reports(cfg)
        t0 = time.time()
        seed = random.randrange(1, 2**31)
        seeds.append(seed)
        code, out, secs = run_cmd(fill(cmd, {"feature_tag": feature.tag, "feature": feature.name, "run": i + 1, "seed": seed}),
                                  cfg, f"run {i + 1}/{runs} seed {seed}")
        res = parse_junit(cfg, t0)
        if not res:
            invalid_runs += 1
            warn(f"Run {i + 1}: no results (exit {code}).\n{out[-1500:]}")
            continue
        for t in tests:
            hist[t["key"]].append(status_for(t, res, raw=True) or "missing")
    flaky, failing, missing, rt_skipped = [], [], [], []
    for k, h in hist.items():
        s = set(h)
        if "skipped" in s:
            rt_skipped.append({"key": k, "history": h})
        if not h or s == {"missing"}:
            missing.append(k)
        elif "passed_on_rerun" in s or ("passed" in s and (s & {"failed", "error"})):
            flaky.append({"key": k, "history": h})
        elif s <= {"failed", "error", "missing"}:
            failing.append({"key": k, "history": h})
    result = {"tool": "qestack.flaky", "created": now_iso(), "feature": feature.name, "runs": runs, "seeds": seeds,
              "invalid_runs": invalid_runs, "status": "INVALID" if invalid_runs == runs else "OK",
              "summary": {"tests": len(tests), "flaky": len(flaky), "failing": len(failing), "missing": len(missing),
                          "skipped_at_runtime": len(rt_skipped)},
              "flaky": flaky, "failing": failing, "missing": missing, "skipped_at_runtime": rt_skipped}
    write_json(feature.runs / "flaky.json", result)
    print(f"flaky: {len(tests)} tests x {runs} runs | flaky={len(flaky)} failing={len(failing)} missing={len(missing)} "
          f"skipped at run time={len(rt_skipped)}")
    for f in flaky:
        print(f"  FLAKY   {f['key']}  {f['history']}  (run seeds: {seeds})")
    for f in failing:
        print(f"  FAILING {f['key']}")
    for f in rt_skipped:
        print(f"  SKIPPED AT RUN TIME {f['key']}  (an assumption, a condition or a missing Docker disabled it)")
    return 0 if not flaky and not failing and not rt_skipped and result["status"] == "OK" else 1


# --------------------------------------------------------------------------------------
# mutation
# --------------------------------------------------------------------------------------


def java_fqn(path: str) -> str | None:
    m = re.search(r"/java/(.+)\.java$", "/" + path)
    return m.group(1).replace("/", ".") if m else None


def newest(pattern: str) -> Path | None:
    hits = globmod.glob(str(ROOT / pattern), recursive=True)
    return Path(max(hits, key=os.path.getmtime)) if hits else None


def parse_pit(p: Path, changed_src):
    by_fqn = {java_fqn(f): f for f in changed_src if java_fqn(f)}
    muts = []
    root = ET.parse(p).getroot()
    for m in root.iter("mutation"):
        cls = (m.findtext("mutatedClass") or "").split("$")[0]
        f = by_fqn.get(cls)
        if changed_src and f is None:
            continue
        st = (m.get("status") or "").upper()
        if st in ("KILLED", "TIMED_OUT", "MEMORY_ERROR"):
            s = "killed"
        elif st in ("SURVIVED", "NO_COVERAGE"):
            s = "survived" if st == "SURVIVED" else "no_coverage"
        else:
            continue
        muts.append({"file": f or cls, "line": int(m.findtext("lineNumber") or 0),
                     "method": m.findtext("mutatedMethod") or "",
                     "mutator": (m.findtext("mutator") or "").split(".")[-1],
                     "description": m.findtext("description") or "", "status": s})
    return muts


def parse_stryker(p: Path, changed_src):
    data = json.loads(p.read_text(encoding="utf-8"))
    muts = []
    changed = set(changed_src)
    for fpath, fdata in (data.get("files") or {}).items():
        rp = rel(fpath) if os.path.isabs(fpath) else fpath.replace("\\", "/")
        if changed and not any(rp.endswith(c) or c.endswith(rp) for c in changed):
            continue
        for m in fdata.get("mutants", []):
            st = m.get("status", "")
            if st in ("Killed", "Timeout"):
                s = "killed"
            elif st == "Survived":
                s = "survived"
            elif st == "NoCoverage":
                s = "no_coverage"
            else:
                continue
            loc = (m.get("location") or {}).get("start") or {}
            muts.append({"file": rp, "line": int(loc.get("line", 0)), "method": "",
                         "mutator": m.get("mutatorName", ""), "description": m.get("replacement", "") or m.get("description", ""),
                         "status": s})
    return muts


def cmd_mutation(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    base = resolve_base(cfg, args.base)
    src_globs = cfg.get_path("paths.source_globs", [])
    exc = cfg.get_path("paths.exclude_globs", [])
    if args.all_files:
        changed_src = []
    else:
        changed_src = [f for f in changed_files(base) if matches_any(f, src_globs) and not matches_any(f, exc) and (ROOT / f).exists()]
        if not changed_src:
            result = {"tool": "qestack.mutation", "created": now_iso(), "feature": feature.name, "status": "NO_CHANGES",
                      "base": base, "summary": {"score": None}, "survivors": []}
            write_json(feature.runs / "mutation.json", result)
            print("mutation: no changed source files; gate is N/A")
            return 0
    fqns = [java_fqn(f) for f in changed_src if java_fqn(f)]
    feature_tests = scope_tests(scan_all_tests(cfg), feature)
    test_fqns = sorted({java_fqn(t["file"]) for t in feature_tests if java_fqn(t["file"])})
    mapping = {
        "target_classes": ",".join(f"{c}*" for c in fqns),
        "feature_test_classes": ",".join(f"{c}*" for c in test_fqns),
        "changed_files": " ".join(shlex.quote(f) for f in changed_src),
        "changed_files_csv": ",".join(changed_src),
        "base_ref": base or "", "feature_tag": feature.tag, "feature": feature.name,
    }
    t0 = time.time()
    code, out = 0, ""
    if not args.skip_run:
        code, out, secs = run_cmd(fill(cfg.get_path("commands.mutation", ""), mapping), cfg, "mutation")
    fmt = cfg.get_path("reports.mutation_format", "pit-xml")
    reports = [Path(p) for p in globmod.glob(str(ROOT / cfg.get_path("reports.mutation_path", "")), recursive=True)]
    if not args.skip_run:
        reports = [p for p in reports if os.path.getmtime(p) >= t0 - 2]  # one report for each module of this run
    if not reports:
        print(out[-3000:])
        die("Mutation report not found or not updated. Check reports.mutation_path and the mutation command.", 1)
    rp = max(reports, key=os.path.getmtime)
    muts = []
    for p in sorted(reports):
        muts += parse_pit(p, changed_src) if fmt == "pit-xml" else parse_stryker(p, changed_src)
    eq = read_json(feature.locks / f"{feature.name}.equivalent.json", []) or []
    eq_keys = {(e.get("file"), int(e.get("line", 0)), e.get("mutator")) for e in eq}
    kept, excluded = [], 0
    for m in muts:
        if (m["file"], m["line"], m["mutator"]) in eq_keys:
            excluded += 1
        else:
            kept.append(m)
    killed = sum(m["status"] == "killed" for m in kept)
    surv = [m for m in kept if m["status"] != "killed"]
    total = len(kept)
    score = round(killed / total, 4) if total else None
    by_file = {}
    for m in kept:
        bf = by_file.setdefault(m["file"], {"killed": 0, "total": 0})
        bf["total"] += 1
        bf["killed"] += m["status"] == "killed"
    result = {"tool": "qestack.mutation", "created": now_iso(), "feature": feature.name, "status": "OK" if total else "NO_MUTANTS",
              "base": base, "report": rel(rp), "reports": [rel(p) for p in sorted(reports)], "changed_source_files": changed_src,
              "summary": {"score": score, "killed": killed, "survived": sum(m["status"] == "survived" for m in surv),
                          "no_coverage": sum(m["status"] == "no_coverage" for m in surv), "total": total,
                          "equivalent_excluded": excluded},
              "by_file": by_file,
              "survivors": sorted(surv, key=lambda m: (m["file"], m["line"]))}
    write_json(feature.runs / "mutation.json", result)
    print(f"mutation: score={'n/a' if score is None else f'{score:.0%}'} killed={killed}/{total} "
          f"survived={result['summary']['survived']} no_coverage={result['summary']['no_coverage']} (equivalent excluded: {excluded})")
    for m in result["survivors"][: args.max]:
        print(f"  SURVIVED {m['file']}:{m['line']} {m['mutator']} - {m['description']}")
    thr = cfg.get_path("gates.mutation_min", 0.75)
    return 0 if score is None or score >= thr else 1


# --------------------------------------------------------------------------------------
# seed (seeded-fault detection)
# --------------------------------------------------------------------------------------


def run_feature_tests(cfg: Cfg, feature: Feature, tests, label: str):
    clean_reports(cfg)
    t0 = time.time()
    code, out, secs = run_cmd(fill(cfg.get_path("commands.test_feature", ""), {"feature_tag": feature.tag, "feature": feature.name}), cfg, label)
    res = parse_junit(cfg, t0)
    failed = {t["key"] for t in tests if status_for(t, res) in ("failed", "error")}
    return code, out, res, failed


def holdout_ids(cfg: Cfg, feature: Feature, ids, catalog) -> set:
    """Stable choice of held-out faults. A catalog entry can set "holdout" explicitly."""
    fixed = {i for i in ids if isinstance(catalog.get(i, {}).get("holdout"), bool)}
    chosen = {i for i in fixed if catalog[i]["holdout"]}
    free = sorted((i for i in ids if i not in fixed), key=lambda i: hashlib.sha256(f"{feature.name}:{i}".encode()).hexdigest())
    n = round(len(ids) * cfg.get_path("loop.holdout_ratio", 0.4)) - len(chosen)
    return chosen | set(free[:max(0, n)])


def recover_applied_fault(fdir: Path) -> None:
    """Revert a fault patch that a killed 'seed' run left in the production code."""
    marker = fdir / ".applied"
    if not marker.exists():
        return
    p = fdir / marker.read_text(encoding="utf-8").strip()
    if p.exists() and git("apply", "-R", "--check", str(p)).returncode == 0:
        git("apply", "-R", str(p))
        warn(f"An earlier seed run stopped with fault {p.stem} applied. The fault is now reverted.")
    marker.unlink()


def cmd_seed(args, cfg):
    import signal
    feature = resolve_feature(cfg, args.feature, strict=True)
    fdir = feature.runs / "faults"
    recover_applied_fault(fdir)
    patches = sorted(fdir.glob("*.patch"))
    catalog = {c.get("id"): c for c in (read_json(fdir / "catalog.json", []) or [])}
    if not patches:
        result = {"tool": "qestack.seed", "created": now_iso(), "feature": feature.name, "status": "NOT_RUN",
                  "summary": {"valid": 0, "detected": 0, "rate": None}, "faults": []}
        write_json(feature.runs / "seed.json", result)
        print("seed: no fault patches found (run the fault seeder first)")
        return 1
    tests = [t for t in scope_tests(scan_all_tests(cfg), feature) if not t["skipped"]]
    compile_cmd = cfg.get_path("commands.compile", "")
    baseline_failed = set()
    if not args.no_baseline:
        code, out, res, baseline_failed = run_feature_tests(cfg, feature, tests, "baseline")
        if not res:
            print(out[-2000:])
            die("Baseline run produced no results. Fix the build first.", 1)
        if baseline_failed:
            warn(f"{len(baseline_failed)} test(s) already fail without faults; they do not count as detection.")
    results = []
    marker = fdir / ".applied"

    def on_term(signum, frame):
        recover_applied_fault(fdir)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, on_term)
    for p in patches:
        fid = p.stem
        meta = catalog.get(fid, {})
        entry = {"id": fid, "patch": rel(p), "req_id": meta.get("req_id"), "layer": meta.get("layer"),
                 "description": meta.get("description", ""), "file": meta.get("file")}
        chk = git("apply", "--check", str(p))
        if chk.returncode != 0:
            entry.update(status="INVALID", reason="patch does not apply: " + chk.stderr.strip()[:300])
            results.append(entry)
            continue
        marker.write_text(p.name, encoding="utf-8")
        git("apply", str(p), check=True)
        try:
            if compile_cmd:
                c_code, c_out, _ = run_cmd(compile_cmd, cfg, f"compile {fid}")
                if c_code != 0:
                    entry.update(status="INVALID", reason="does not compile with the fault")
                    results.append(entry)
                    continue
            code, out, res, failed = run_feature_tests(cfg, feature, tests, f"fault {fid}")
            if not res:
                entry.update(status="INVALID", reason=f"no test results (exit {code})")
            else:
                newly = sorted(failed - baseline_failed)
                entry.update(status="DETECTED" if newly else "UNDETECTED", detected_by=newly[:20])
            results.append(entry)
        finally:
            rv = git("apply", "-R", str(p))
            if rv.returncode != 0:
                die(f"Could not revert fault patch {rel(p)}: {rv.stderr}. Restore the files with git before you continue.")
            marker.unlink(missing_ok=True)
    holdout = holdout_ids(cfg, feature, [r["id"] for r in results], catalog)
    for r in results:
        r["holdout"] = r["id"] in holdout

    def rate_of(rs):
        v = [r for r in rs if r["status"] != "INVALID"]
        d = [r for r in v if r["status"] == "DETECTED"]
        return len(v), len(d), (round(len(d) / len(v), 4) if v else None)

    n_valid, n_det, all_rate = rate_of(results)
    h_valid, h_det, h_rate = rate_of([r for r in results if r["holdout"]])
    f_valid, f_det, f_rate = rate_of([r for r in results if not r["holdout"]])
    use_holdout = h_valid >= cfg.get_path("loop.holdout_min", 2)
    rate = h_rate if use_holdout else all_rate
    summary = {"faults": len(results), "valid": n_valid, "detected": n_det, "rate": rate,
               "rate_basis": "holdout" if use_holdout else "all", "all_rate": all_rate,
               "holdout_valid": h_valid, "holdout_detected": h_det, "holdout_rate": h_rate,
               "feedback_valid": f_valid, "feedback_detected": f_det, "feedback_rate": f_rate,
               "baseline_failing": len(baseline_failed)}
    result = {"tool": "qestack.seed", "created": now_iso(), "feature": feature.name,
              "status": "OK" if n_valid else "NO_VALID_FAULTS", "summary": summary, "faults": results}
    write_json(feature.runs / "seed.json", result)
    # Redacted version for the test writer and the judge: no fault details, no held-out faults.
    redacted = [{"id": r["id"], "req_id": r.get("req_id"), "layer": r.get("layer"), "status": r["status"]}
                for r in results if not r["holdout"]]
    write_json(feature.runs / "seed-feedback.json", {"feature": feature.name, "summary": summary, "faults": redacted})
    print(f"seed: detected {n_det}/{n_valid} valid faults ({'n/a' if all_rate is None else f'{all_rate:.0%}'}); "
          f"held out {h_det}/{h_valid}; gate uses {summary['rate_basis']} ({'n/a' if rate is None else f'{rate:.0%}'}); "
          f"invalid={len(results) - n_valid}")
    for r in results:
        if r["status"] != "DETECTED" and not r["holdout"]:
            print(f"  {r['status']:<10} {r['id']} [{r.get('req_id') or '-'}] {r.get('reason', '')}")
    thr = cfg.get_path("gates.seed_min", 0.9)
    return 0 if rate is not None and rate >= thr else 1


# --------------------------------------------------------------------------------------
# guard / lock / snapshot / hook
# --------------------------------------------------------------------------------------

RANK = {"OK": 4, "SHALLOW": 3, "TRIVIAL": 2, "NO_ASSERTION": 1, "HOLLOW": 0}


def method_snapshot(tests):
    snap = {}
    for t in tests:
        k = f"{t['class']}.{t['method']}"
        snap[k] = {"assertions": t["assertions"], "strong": t["strong"], "classification": t["classification"],
                   "skipped": t["skipped"], "ids": t["ids"], "line": t["line"],
                   "statements_hash": hashlib.sha256("\n".join(t["assertion_statements"]).encode()).hexdigest()[:16]}
    return snap


def compare_snapshots(old: dict, new: dict, path: str):
    """Return (violations, reviews)."""
    v, r = [], []
    for k, o in old.items():
        n = new.get(k)
        where = f"{path}::{k}"
        if n is None:
            v.append({"type": "TEST_REMOVED", "test": where, "detail": "test method removed or renamed"})
            continue
        if n["skipped"] and not o["skipped"]:
            v.append({"type": "SKIP_ADDED", "test": where, "detail": "skip/disable added"})
        if n["assertions"] < o["assertions"]:
            v.append({"type": "ASSERTIONS_REDUCED", "test": where, "detail": f"{o['assertions']} -> {n['assertions']}"})
        elif n["strong"] < o["strong"]:
            v.append({"type": "ASSERTIONS_WEAKENED", "test": where, "detail": f"strong assertions {o['strong']} -> {n['strong']}"})
        if RANK.get(n["classification"], 0) < RANK.get(o["classification"], 0):
            v.append({"type": "CLASSIFICATION_WORSE", "test": where, "detail": f"{o['classification']} -> {n['classification']}"})
        lost = sorted(set(o["ids"]) - set(n["ids"]))
        if lost:
            v.append({"type": "TRACE_REMOVED", "test": where, "detail": "removed IDs: " + ", ".join(lost)})
        if n["statements_hash"] != o["statements_hash"] and n["assertions"] >= o["assertions"]:
            r.append({"type": "ASSERTION_CHANGED", "test": where, "detail": "assertion text changed; check that the oracle still follows the spec"})
    return v, r


def file_snapshot(cfg: Cfg, path: str, text: str | None = None):
    lang = Lang(cfg)
    if text is None:
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
    return method_snapshot(parse_tests(lang, text, path)), hashlib.sha256(text.encode()).hexdigest()


def lock_path(feature: Feature) -> Path:
    return feature.locks / f"{feature.name}.json"


def all_locks(cfg: Cfg):
    d = ROOT / cfg.get_path("paths.locks_dir", ".qestack/locks")
    out = {}
    if d.exists():
        for p in d.glob("*.json"):
            if p.name.count(".") > 1:  # *.equivalent.json, *.red-exempt.json
                continue
            data = read_json(p, {}) or {}
            for f, entry in (data.get("files") or {}).items():
                out[f] = entry
    return out


def cmd_lock(args, cfg):
    feature = resolve_feature(cfg, args.feature, strict=True)
    tests = scope_tests(scan_all_tests(cfg), feature)
    files = sorted({t["file"] for t in tests})
    if not files:
        die(f"No tests with tag '{feature.tag}' to lock.")
    lp = lock_path(feature)
    old = read_json(lp, {}) or {}
    new_files = {}
    violations = []
    for f in files:
        snap, sha = file_snapshot(cfg, f)
        if f in (old.get("files") or {}):
            v, _ = compare_snapshots(old["files"][f]["methods"], snap, f)
            violations += v
        new_files[f] = {"sha256": sha, "methods": snap}
    for f in (old.get("files") or {}):
        if f not in new_files:
            if (ROOT / f).exists():
                snap, sha = file_snapshot(cfg, f)
                v, _ = compare_snapshots(old["files"][f]["methods"], snap, f)
                violations += v
                new_files[f] = {"sha256": sha, "methods": snap}
            else:
                violations.append({"type": "TEST_FILE_REMOVED", "test": f, "detail": "locked test file deleted"})
    if violations and not args.force:
        for v in violations:
            print(f"  {v['type']}: {v['test']} ({v['detail']})")
        die("Lock update refused: the change weakens locked tests. A human can re-lock with --force.", 1)
    data = {"feature": feature.name, "feature_tag": feature.tag, "created": old.get("created", now_iso()),
            "updated": now_iso(), "git_head": git_head(), "phase": args.phase or old.get("phase", ""),
            "files": new_files}
    write_json(lp, data)
    n_methods = sum(len(v["methods"]) for v in new_files.values())
    print(f"lock: {len(new_files)} file(s), {n_methods} test method(s) locked -> {rel(lp)}")
    return 0


def cmd_snapshot(args, cfg):
    feature = resolve_feature(cfg, args.feature, strict=True)
    files = find_files(cfg, "source_globs")
    data = {"created": now_iso(), "git_head": git_head(),
            "files": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}}
    write_json(feature.runs / "source-snapshot.json", data)
    print(f"snapshot: {len(files)} source file(s) recorded")
    return 0


def cmd_guard(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    base = resolve_base(cfg, args.base)
    violations, reviews = [], []
    test_globs = cfg.get_path("paths.test_globs", [])
    changed = changed_files(base) if base else []
    if not base:
        warn("No base ref found; only lock and snapshot checks run.")
    # 1. protected files
    locks_prefix = cfg.get_path("paths.locks_dir", ".qestack/locks").rstrip("/") + "/"
    for f in changed:
        if f.startswith(locks_prefix):
            human_only = f.endswith(".equivalent.json") or f.endswith(".red-exempt.json")
            reviews.append({"type": "HUMAN_DECISION_FILE_CHANGED" if human_only else "LOCK_CHANGED", "test": f,
                            "detail": "a human must approve this change" if human_only else "test lock created or updated by qestack lock"})
        elif is_protected(cfg, f):
            item = {"type": "PROTECTED_FILE_CHANGED", "test": f, "detail": "protected file changed (thresholds, rubrics, tools)"}
            (reviews if args.allow_protected else violations).append(item)
    # 2. weakening vs base
    for f in changed:
        if not matches_any(f, test_globs):
            continue
        old_text = git_show(base, f) if base else None
        if old_text is None:
            continue
        if not (ROOT / f).exists():
            old_snap, _ = file_snapshot(cfg, f, old_text)
            if old_snap:
                violations.append({"type": "TEST_FILE_REMOVED", "test": f, "detail": f"{len(old_snap)} test(s) deleted"})
            continue
        old_snap, _ = file_snapshot(cfg, f, old_text)
        new_snap, _ = file_snapshot(cfg, f)
        v, r = compare_snapshots(old_snap, new_snap, f)
        violations += [dict(x, against="base") for x in v]
        reviews += [dict(x, against="base") for x in r]
    # 3. weakening vs lock
    lock = read_json(lock_path(feature), {}) or {}
    for f, entry in (lock.get("files") or {}).items():
        if not (ROOT / f).exists():
            violations.append({"type": "TEST_FILE_REMOVED", "test": f, "detail": "locked test file deleted", "against": "lock"})
            continue
        new_snap, sha = file_snapshot(cfg, f)
        if sha == entry.get("sha256"):
            continue
        v, r = compare_snapshots(entry["methods"], new_snap, f)
        known = {(x["type"], x["test"]) for x in violations}
        violations += [dict(x, against="lock") for x in v if (x["type"], x["test"]) not in known]
        reviews += [dict(x, against="lock") for x in r]
    # 4. production code must not change during a test-only phase
    if args.source_unchanged:
        snap = read_json(feature.runs / "source-snapshot.json")
        if not snap:
            warn("No source snapshot; run 'qestack snapshot' before the test-only phase.")
        else:
            stubs = set(read_json(feature.runs / "stubs.json", []) or [])
            cur = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in find_files(cfg, "source_globs")}
            for f in sorted(set(cur) | set(snap["files"])):
                if cur.get(f) == snap["files"].get(f):
                    continue
                if f in stubs and f not in snap["files"]:
                    continue  # a new stub file
                if f in stubs:
                    # The writer lists the stubs itself, so a stub in an existing file needs a human check.
                    reviews.append({"type": "STUB_IN_EXISTING_FILE", "test": f,
                                    "detail": "check that the change only adds stub members"})
                    continue
                violations.append({"type": "SOURCE_CHANGED_IN_TEST_PHASE", "test": f, "detail": "production code changed by a test-only phase"})
    # dedupe reviews
    seen, rv = set(), []
    for x in reviews:
        k = (x["type"], x["test"])
        if k not in seen:
            seen.add(k)
            rv.append(x)
    result = {"tool": "qestack.guard", "created": now_iso(), "feature": feature.name, "base": base,
              "summary": {"violations": len(violations), "reviews": len(rv)}, "violations": violations, "reviews": rv}
    write_json(feature.runs / "guard.json", result)
    print(f"guard: violations={len(violations)} human-review items={len(rv)} (base={base or 'none'})")
    for x in violations:
        print(f"  VIOLATION {x['type']}: {x['test']} ({x['detail']})")
    for x in rv[: args.max]:
        print(f"  REVIEW    {x['type']}: {x['test']}")
    return 1 if violations else 0


def _apply_edit(cur: str, old: str, new: str, replace_all: bool) -> str:
    if old == "":
        return new
    return cur.replace(old, new) if replace_all else cur.replace(old, new, 1)


def _block(msg: str):
    sys.stderr.write("[qestack guard] BLOCKED: " + msg + "\n")
    sys.exit(2)


ENGINE_OUTPUTS = {"lint.json", "trace.json", "trace-plan.json", "red.json", "flaky.json", "mutation.json", "seed.json",
                  "seed-feedback.json", "guard.json", "scorecard.json", "judge-basis.json", "source-snapshot.json",
                  "calibration.json", "history.jsonl", "quality-report.md"}


def engine_output(cfg: Cfg, rp: str) -> bool:
    """True for files that only the engine writes. Agents must not forge gate results."""
    runs = cfg.get_path("paths.runs_dir", ".qestack/runs").rstrip("/") + "/"
    specs = cfg.get_path("paths.specs_dir", "specs").rstrip("/") + "/"
    name = rp.rsplit("/", 1)[-1]
    if rp.startswith(specs):
        return name == "quality-report.md"
    if not rp.startswith(runs):
        return False
    if "/faults/" in rp:
        return name != "fault-review.json"  # patches, catalog, clean copy: only 'qestack fault' writes them
    return name in ENGINE_OUTPUTS or bool(re.match(r"feedback-\d+\.md$", name))


def cmd_hook(args, cfg_unused=None):
    """Claude Code PreToolUse hook. Exit 2 blocks the tool call. Fails open on internal errors."""
    raw = sys.stdin.read()
    log = os.environ.get("QESTACK_HOOK_LOG")
    if log:  # to check which fields Claude Code sends (for example the agent identity)
        try:
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(raw.strip() + "\n")
        except OSError:
            pass
    try:
        data = json.loads(raw)
    except Exception:
        return 0
    if not (QE_DIR / "project.toml").exists():
        return 0  # not a qestack project: allow everything
    try:
        cfg = load_config()
    except (SystemExit, Exception):
        return 0
    try:
        tool = data.get("tool_name", "")
        ti = data.get("tool_input") or {}
        if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
            path = ti.get("file_path") or ti.get("notebook_path") or ""
            if not path:
                return 0
            p = Path(path)
            if not p.is_absolute():
                p = Path(data.get("cwd") or ROOT) / p
            try:
                p.resolve().relative_to(PKG_DIR)
                _block("This file belongs to the installed qestack engine. Agents must not change it.")
            except ValueError:
                pass
            rp = rel(p)
            if rp.startswith("/") or rp.startswith(".."):
                return 0
            if engine_output(cfg, rp):
                _block(f"'{rp}' is a result file of the qestack engine. Only qestack commands write it. "
                       "Run the qestack command again instead of editing the result.")
            if is_protected(cfg, rp):
                _block(f"'{rp}' is a protected qestack file (settings, thresholds, rubrics, locks). "
                       "Agents must not change it. Ask the user to make this change.")
            locks = all_locks(cfg)
            if rp in locks and p.exists():
                cur = p.read_text(encoding="utf-8", errors="replace")
                if tool == "Write":
                    new = ti.get("content", "")
                elif tool == "Edit":
                    new = _apply_edit(cur, ti.get("old_string", ""), ti.get("new_string", ""), bool(ti.get("replace_all")))
                elif tool == "MultiEdit":
                    new = cur
                    for e in ti.get("edits", []):
                        new = _apply_edit(new, e.get("old_string", ""), e.get("new_string", ""), bool(e.get("replace_all")))
                else:
                    return 0
                old_snap, _ = file_snapshot(cfg, rp, cur)
                new_snap, _ = file_snapshot(cfg, rp, new)
                v, _ = compare_snapshots(old_snap, new_snap, rp)
                if v:
                    lines = "; ".join(f"{x['type']} {x['test'].split('::')[-1]} ({x['detail']})" for x in v[:8])
                    _block(f"'{rp}' contains locked tests. This edit weakens them: {lines}. "
                           "You may add tests or strengthen assertions. You must not remove tests, remove assertions, "
                           "add skips or remove requirement tags. If a locked test is wrong, record it in "
                           "suspected-test-defects.md and ask the user.")
        elif tool == "Bash":
            cmd = ti.get("command", "") or ""
            if re.search(r"\bqestack\s+lock\b.*--force", cmd):
                _block("Only a human may force a lock update (qestack lock --force).")
            scrubbed = re.sub(r"\d?>&\d|\d?>\s*/dev/null", " ", cmd)
            write_ops = re.compile(r"(>|\btee\b|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i|\bperl\s+-\S*i|\btruncate\b|\bchmod\b|\bln\b|"
                                   r"\bgit\s+(?:checkout|restore|rm|mv)\b|\bpython3?\s+-c\b|\bdd\b)")
            if write_ops.search(scrubbed):
                for pat in cfg.get_path("paths.protected", []):
                    prefix = pat.split("*")[0].rstrip("/")
                    if prefix and len(prefix) > 6 and prefix in scrubbed:
                        _block(f"This shell command may change the protected path '{prefix}'. Agents must not change it.")
                for f in all_locks(cfg):
                    if f in scrubbed or (len(Path(f).name) > 8 and re.search(r"(?<![\w.])" + re.escape(Path(f).name) + r"\b", scrubbed)):
                        _block(f"This shell command may change the locked test file '{f}'. Use Edit to strengthen the tests; "
                               "the guard checks Edit and Write.")
                for tok in re.findall(r"[\w./-]+", scrubbed):
                    if engine_output(cfg, rel(Path(data.get("cwd") or ROOT) / tok) if not tok.startswith("/") else rel(Path(tok))):
                        _block(f"This shell command may change the qestack result file '{tok}'. Only qestack commands write it.")
    except SystemExit:
        raise
    except Exception as e:  # fail open, but say so
        sys.stderr.write(f"[qestack guard] hook error (allowed): {e}\n")
    return 0


# --------------------------------------------------------------------------------------
# judge validation, score, report, feedback
# --------------------------------------------------------------------------------------

DIMS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
EVIDENCE_RX = re.compile(r"(\S+:\d+)|(\S+\.md#\S+)")


def judge_rules(scores: dict) -> str:
    vals = [scores.get(d) for d in DIMS if isinstance(scores.get(d), (int, float))]
    if not vals or any(v == 0 for v in vals):
        return "reject"
    if (any(v <= 1 for v in vals) or scores.get("R1", 0) < 3 or scores.get("R2", 0) < 3 or scores.get("R3", 0) < 3
            or (sum(vals) / len(vals)) < 2.5):
        return "revise"
    return "accept"


def judge_basis(feature: Feature, tests, ci: bool):
    """Return keys of tests that changed after the judge review (or None if unknown)."""
    jp = feature.runs / "judge.json"
    jsha = hashlib.sha256(jp.read_bytes()).hexdigest()
    bp = feature.runs / "judge-basis.json"
    basis = read_json(bp)
    cur = {t["key"]: t.get("body_hash") for t in tests}
    if not basis or basis.get("judge_sha") != jsha:
        if ci:
            return set(cur)  # no record of what the judge saw: treat all as unreviewed
        write_json(bp, {"judge_sha": jsha, "created": now_iso(), "tests": cur})
        return set()
    old = basis.get("tests", {})
    return {k for k, h in cur.items() if k in old and old[k] != h}


def load_judge(feature: Feature, tests, ci: bool = False):
    j = read_json(feature.runs / "judge.json")
    if not j:
        return None
    order = {"accept": 0, "revise": 1, "reject": 2}
    keys = {t["key"] for t in tests}
    out = {"raw": j, "tests": {}, "invalid": [], "unreviewed": []}
    for e in j.get("tests", []):
        k = e.get("key")
        sc, invalid = {}, []
        for d in DIMS:
            v = (e.get("scores") or {}).get(d)
            if isinstance(v, dict):
                s, ev = v.get("score"), v.get("evidence", "")
            else:
                s, ev = v, ""
            if not isinstance(s, (int, float)) or not 0 <= s <= 4:
                invalid.append(f"{d}: missing or out-of-range score")
                continue
            if not (isinstance(ev, str) and EVIDENCE_RX.search(ev)):
                invalid.append(f"{d}: no file:line evidence")
            sc[d] = s
        rule_v = judge_rules(sc) if len(sc) == len(DIMS) else "reject"
        given = (e.get("verdict") or "revise").lower()
        verdict = max([rule_v, given], key=lambda x: order.get(x, 1))
        out["tests"][k] = {"scores": sc, "verdict": verdict, "given_verdict": given, "rule_verdict": rule_v,
                           "findings": e.get("findings", []), "invalid": invalid}
        if invalid:
            out["invalid"].append({"key": k, "problems": invalid})
    stale = judge_basis(feature, tests, ci)
    out["stale"] = sorted(stale)
    out["unreviewed"] = sorted((keys - set(out["tests"])) | stale)
    return out


def wavg(pairs):
    pairs = [(v, w) for v, w in pairs if v is not None]
    tw = sum(w for _, w in pairs)
    return (sum(v * w for v, w in pairs) / tw) if tw else None


def gate(name, status, value, target, note=""):
    return {"gate": name, "status": status, "value": value, "target": target, "note": note}


def compute_score(cfg: Cfg, feature: Feature, ci: bool = False):
    G = cfg.get("gates", {})
    W = cfg.get("weights", {})
    R = feature.runs
    lint = read_json(R / "lint.json")
    trace = read_json(R / "trace.json")
    red = read_json(R / "red.json")
    flaky = read_json(R / "flaky.json")
    mut = read_json(R / "mutation.json")
    seed = read_json(R / "seed.json")
    if seed is None:  # CI: fault patches are not committed; use the redacted summary
        sf = read_json(R / "seed-feedback.json")
        if sf:
            seed = {"status": "OK", "summary": sf.get("summary", {}),
                    "faults": [dict(f, description="(details hidden)") for f in sf.get("faults", [])]}
    guard = read_json(R / "guard.json")
    tests = (lint or {}).get("tests", [])
    judge = load_judge(feature, tests, ci) if lint else None
    gates = []

    def nr(name, target):
        gates.append(gate(name, "NOT_RUN", None, target))

    if lint:
        s = lint["summary"]
        gates.append(gate("hollow", "PASS" if s["hollow"] <= G.get("hollow_max", 0) else "FAIL", s["hollow"], f"<= {G.get('hollow_max', 0)}"))
        gates.append(gate("no_assertion", "PASS" if s["no_assertion"] <= G.get("no_assertion_max", 0) else "FAIL", s["no_assertion"], f"<= {G.get('no_assertion_max', 0)}"))
        rt_skipped = len((flaky or {}).get("skipped_at_runtime", []))
        n_skip = s["skipped"] + rt_skipped
        gates.append(gate("skipped", "PASS" if n_skip <= G.get("skipped_max", 0) else "FAIL", n_skip, f"<= {G.get('skipped_max', 0)}",
                          f"{rt_skipped} skipped at run time" if rt_skipped else ""))
        for g in ("trivial", "shallow"):
            gates.append(gate(g, "PASS" if s[g] <= G.get(f"{g}_max", 0) else "FAIL", s[g], f"<= {G.get(f'{g}_max', 0)}"))
        if s["total"] == 0:
            gates.append(gate("tests_exist", "FAIL", 0, "> 0", f"no tests tagged {feature.tag}"))
    else:
        for g in ("hollow", "no_assertion", "skipped", "trivial", "shallow"):
            nr(g, 0)
    if trace:
        c = trace["summary"]["coverage"]
        gates.append(gate("trace", "PASS" if c >= G.get("trace_coverage_min", 1.0) and trace["summary"]["required_total"] > 0 else "FAIL",
                          c, f">= {G.get('trace_coverage_min', 1.0):.0%}", "" if trace["summary"]["required_total"] else "no requirement IDs found in spec"))
    else:
        nr("trace", G.get("trace_coverage_min", 1.0))
    if red:
        rr = red["summary"]["rate"]
        ok = red["status"] == "OK" and rr >= G.get("red_min", 1.0) and red["summary"]["not_run"] == 0
        gates.append(gate("red", "PASS" if ok else "FAIL", rr, f">= {G.get('red_min', 1.0):.0%}", red["status"]))
    else:
        nr("red", G.get("red_min", 1.0))
    if flaky:
        nf, nfail = flaky["summary"]["flaky"], flaky["summary"]["failing"]
        gates.append(gate("flaky", "PASS" if nf <= G.get("flaky_max", 0) and flaky["status"] == "OK" else "FAIL", nf, f"<= {G.get('flaky_max', 0)}"))
        gates.append(gate("failing", "PASS" if nfail <= G.get("failing_max", 0) else "FAIL", nfail, f"<= {G.get('failing_max', 0)}",
                          "each failing test is a test defect or a product bug"))
    else:
        nr("flaky", 0)
        nr("failing", 0)
    mscore = None
    if mut:
        mscore = mut["summary"]["score"]
        if mut["status"] == "NO_CHANGES":
            gates.append(gate("mutation", "N_A", None, f">= {G.get('mutation_min', 0.75):.0%}", "no changed source files"))
        else:
            gates.append(gate("mutation", "PASS" if mscore is not None and mscore >= G.get("mutation_min", 0.75) else "FAIL",
                              mscore, f">= {G.get('mutation_min', 0.75):.0%}"))
    else:
        nr("mutation", G.get("mutation_min", 0.75))
    srate = None
    if seed and seed.get("status") not in ("NOT_RUN",):
        srate = seed["summary"]["rate"]
        gates.append(gate("seed", "PASS" if srate is not None and srate >= G.get("seed_min", 0.9) else "FAIL", srate, f">= {G.get('seed_min', 0.9):.0%}"))
    else:
        nr("seed", G.get("seed_min", 0.9))
    if guard:
        gv = guard["summary"]["violations"]
        gates.append(gate("guard", "PASS" if gv <= G.get("guard_violations_max", 0) else "FAIL", gv, f"<= {G.get('guard_violations_max', 0)}"))
    else:
        nr("guard", 0)
    if judge:
        rej = sum(1 for v in judge["tests"].values() if v["verdict"] == "reject")
        cov = (len(tests) - len(judge["unreviewed"])) / max(1, len(tests))
        ok = rej <= G.get("judge_rejects_max", 0) and cov >= G.get("judge_coverage_min", 1.0) and not judge["invalid"]
        note = f"rejects={rej}, reviewed={cov:.0%}, invalid entries={len(judge['invalid'])}, changed after review={len(judge['stale'])}"
        gates.append(gate("judge", "PASS" if ok else "FAIL", rej, f"rejects <= {G.get('judge_rejects_max', 0)}, reviewed 100%", note))
    else:
        nr("judge", 0)

    required = set(G.get("required", []))
    for g in gates:
        if g["status"] == "NOT_RUN" and g["gate"] not in required:
            g["status"] = "SKIPPED"
            g["note"] = (g["note"] + " (not required)").strip()

    # ---- TQS
    js = list(judge["tests"].values()) if judge else []

    def jmean(dims, scale):
        if not js:
            return None
        vals = [sum(t["scores"].get(d, 0) for d in dims) / scale for t in js if t["scores"]]
        return sum(vals) / len(vals) if vals else None

    lint_strength = (1 - lint["summary"]["weak_rate"]) if lint and lint["summary"]["total"] else None
    smell_ok = (1 - lint["summary"]["smell_rate"]) if lint and lint["summary"]["total"] else None
    dims = {
        "fault_detection": wavg([(mscore, 0.6), (srate, 0.4)]),
        "requirement_depth": trace["summary"]["depth_ratio"] if trace else None,
        "assertion_strength": wavg([(lint_strength, 0.5), (jmean(["R2", "R3"], 8), 0.5)]),
        "independence": jmean(["R5"], 4),
        "maintainability": wavg([(smell_ok, 0.5), (jmean(["R6", "R7"], 8), 0.5)]),
    }
    weights = {k: W.get(k, 0) for k in dims}
    tqs = wavg([(v, weights[k]) for k, v in dims.items()])
    partial = any(v is None for v in dims.values())
    tqs_val = round(100 * tqs, 1) if tqs is not None else None
    tqs_min = G.get("tqs_min", 80)
    hard_fail = [g["gate"] for g in gates if g["status"] in ("FAIL", "NOT_RUN")]
    accepted = not hard_fail and tqs_val is not None and tqs_val >= tqs_min and not partial
    return {
        "feature": feature.name, "created": now_iso(), "tool_version": TOOL_VERSION,
        "gates": gates, "hard_gate_failures": hard_fail,
        "dimensions": {k: (round(100 * v, 1) if v is not None else None) for k, v in dims.items()},
        "weights": weights, "tqs": tqs_val, "tqs_min": tqs_min, "tqs_partial": partial,
        "accepted": accepted, "judge": judge, "inputs": {"lint": lint, "trace": trace, "red": red, "flaky": flaky,
                                                         "mutation": mut, "seed": seed, "guard": guard},
    }


def decide(cfg: Cfg, feature: Feature, sc: dict, iteration: int):
    L = cfg.get("loop", {})
    hist_p = feature.runs / "history.jsonl"
    hist = []
    if hist_p.exists():
        for line in hist_p.read_text().splitlines():
            try:
                hist.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    hist = [h for h in hist if h.get("iteration") != iteration]
    hist.append({"iteration": iteration, "tqs": sc["tqs"], "accepted": sc["accepted"], "failures": sc["hard_gate_failures"], "at": now_iso()})
    hist.sort(key=lambda h: h["iteration"])
    hist_p.parent.mkdir(parents=True, exist_ok=True)
    hist_p.write_text("".join(json.dumps(h) + "\n" for h in hist))
    if sc["accepted"]:
        return "ACCEPT", "all hard gates pass and TQS meets the minimum", hist
    if iteration >= L.get("max_iterations", 4):
        return "ESCALATE", f"maximum iterations ({L.get('max_iterations', 4)}) reached", hist
    pat = L.get("patience", 2)
    if len(hist) > pat:
        prev = hist[-1 - pat]["tqs"] or 0
        cur = hist[-1]["tqs"] or 0
        prev_fail = len(hist[-1 - pat]["failures"])
        cur_fail = len(hist[-1]["failures"])
        if cur - prev < L.get("min_improvement", 2.0) and cur_fail >= prev_fail:
            return "ESCALATE", f"no real improvement in the last {pat} iterations (TQS {prev} -> {cur})", hist
    return "CONTINUE", "improve the tests with the feedback file", hist


def audit_sample(cfg: Cfg, feature: Feature, sc: dict, iteration: int):
    tests = (sc["inputs"]["lint"] or {}).get("tests", [])
    keys = [t["key"] for t in tests]
    L = cfg.get("loop", {})
    rng = random.Random(f"{feature.name}-{iteration}")
    rnd = rng.sample(keys, min(len(keys), L.get("audit_random", 5)))
    low = []
    if sc["judge"]:
        ranked = sorted(sc["judge"]["tests"].items(),
                        key=lambda kv: sum(kv[1]["scores"].values()) / max(1, len(kv[1]["scores"])))
        low = [k for k, _ in ranked if k not in rnd][: L.get("audit_lowest", 5)]
    return rnd, low


def fmt_pct(v):
    return "n/a" if v is None else (f"{v:.0%}" if isinstance(v, float) and v <= 1 else str(v))


def render_report(cfg: Cfg, feature: Feature, sc: dict, decision, reason, hist, iteration: int) -> str:
    I = sc["inputs"]
    L = []
    a = L.append
    a(f"# Test Quality Report: {feature.name}")
    a("")
    a(f"Generated: {sc['created']} | Iteration: {iteration} | Tool: qestack {TOOL_VERSION}")
    a("")
    a(f"## Decision: **{decision}**")
    a("")
    a(f"{reason}.")
    a("")
    a(f"**Test Quality Score: {sc['tqs'] if sc['tqs'] is not None else 'n/a'}** (minimum {sc['tqs_min']})"
      + (" (partial: some inputs are missing)" if sc["tqs_partial"] else ""))
    a("")
    a("## 1. Hard gates")
    a("")
    a("| Gate | Status | Value | Target | Note |")
    a("|---|---|---|---|---|")
    for g in sc["gates"]:
        a(f"| {g['gate']} | {g['status']} | {fmt_pct(g['value'])} | {g['target']} | {g['note']} |")
    a("")
    a("## 2. Score dimensions")
    a("")
    a("| Dimension | Score | Weight |")
    a("|---|---|---|")
    for k, v in sc["dimensions"].items():
        a(f"| {k.replace('_', ' ')} | {v if v is not None else 'n/a'} | {sc['weights'][k]:.0%} |")
    a("")
    if len(hist) > 1:
        a("Trend: " + " -> ".join(f"it{h['iteration']}: {h['tqs']}" for h in hist))
        a("")
    tr = I["trace"]
    if tr:
        a("## 3. Requirement traceability")
        a("")
        s = tr["summary"]
        a(f"Coverage {s['coverage']:.0%} ({s['covered']}/{s['required_total']}), depth {s['depth_ratio']:.0%}, "
          f"orphan tests {s['orphans']}, unknown IDs {s['unknown_ids']}, excluded by test plan {s['excluded_by_plan']}.")
        a("")
        a("| ID | Tests | Categories | Status |")
        a("|---|---|---|---|")
        for r in tr["requirements"]:
            st = "OK" if r["depth_ok"] else ("UNCOVERED" if not r["covered"] else "missing " + ", ".join(r["missing_categories"]))
            if r.get("needs_clarification"):
                st += " (spec needs clarification)"
            a(f"| {r['id']} | {len(r['tests'])} | {', '.join(r['categories_found']) or '-'} | {st} |")
        if tr.get("excluded_by_plan"):
            a("")
            a("Excluded by the test plan (human must confirm): " + ", ".join(x["id"] for x in tr["excluded_by_plan"]))
        a("")
    m = I["mutation"]
    if m and m.get("survivors"):
        a("## 4. Surviving mutants")
        a("")
        a("Each line is a code change that no test detected.")
        a("")
        for s_ in m["survivors"][:40]:
            a(f"- `{s_['file']}:{s_['line']}` {s_['mutator']}: {s_['description']} ({s_['status']})")
        if len(m["survivors"]) > 40:
            a(f"- ... {len(m['survivors']) - 40} more in mutation.json")
        a("")
    sd = I["seed"]
    if sd and sd.get("faults"):
        und = [f for f in sd["faults"] if f["status"] != "DETECTED"]
        if und:
            # Agents can read this report, so it has no fault details and no held-out faults.
            a("## 5. Seeded faults not detected")
            a("")
            for f in und:
                if not f.get("holdout"):
                    a(f"- **{f['id']}** [{f.get('req_id') or '-'} / {f.get('layer') or '-'}] {f['status']}")
            n_hold = sum(1 for f in und if f.get("holdout"))
            if n_hold:
                a(f"- {n_hold} held-out fault(s) not detected")
            fdir = feature.runs / "faults"
            if fdir.exists():
                det = ["# Seeded faults not detected (for humans only; do not give this file to an agent)", ""]
                det += [f"- **{f['id']}**{' (held out)' if f.get('holdout') else ''} [{f.get('req_id') or '-'} / "
                        f"{f.get('layer') or '-'}] {f['status']}: {f.get('description', '')} {f.get('reason', '')}" for f in und]
                (fdir / "undetected.md").write_text("\n".join(det) + "\n", encoding="utf-8")
                a("")
                a(f"Fault details for humans: `{rel(fdir / 'undetected.md')}` (not committed).")
            a("")
    j = sc["judge"]
    if j:
        bad = [(k, v) for k, v in j["tests"].items() if v["verdict"] != "accept"]
        if bad or j["invalid"] or j["unreviewed"]:
            a("## 6. Judge findings")
            a("")
            for k, v in bad[:40]:
                a(f"- **{v['verdict'].upper()}** `{k}`")
                for f in (v.get("findings") or [])[:4]:
                    a(f"  - {f.get('dimension', '')} {f.get('severity', '')}: {f.get('issue', '')} ({f.get('evidence', '')})")
            for x in j["invalid"][:20]:
                a(f"- INVALID JUDGE ENTRY `{x['key']}`: {'; '.join(x['problems'])}")
            if j["unreviewed"]:
                a(f"- Not reviewed by the judge: {len(j['unreviewed'])} test(s)")
            a("")
        bugs = j["raw"].get("suspected_product_bugs") or []
        if bugs:
            a("## 7. Suspected product bugs")
            a("")
            for b in bugs:
                a(f"- {b.get('id', '')} [{b.get('req_id', '')}] {b.get('summary', b)} ({b.get('evidence', '')})")
            a("")
    sb = feature.runs / "suspected-bugs.md"
    if sb.exists() and sb.read_text().strip():
        a("Suspected bugs logged by the test writer: see `" + rel(sb) + "`.")
        a("")
    a("## 8. Items for human decision")
    a("")
    items = 0
    g = I["guard"]
    if g:
        for x in g.get("violations", []):
            a(f"- VIOLATION {x['type']}: `{x['test']}` ({x['detail']})")
            items += 1
        for x in g.get("reviews", [])[:30]:
            a(f"- REVIEW {x['type']}: `{x['test']}`")
            items += 1
    if j and j["raw"].get("equivalent_mutant_candidates"):
        for e in j["raw"]["equivalent_mutant_candidates"]:
            a(f"- Equivalent mutant candidate `{e.get('file')}:{e.get('line')}` {e.get('mutator')}: {e.get('reason', '')} "
              f"(add to `{rel(feature.locks / (feature.name + '.equivalent.json'))}` only if you agree)")
            items += 1
    rd = I["red"]
    if rd and rd.get("violations"):
        for k in rd["violations"]:
            a(f"- Test passed before implementation: `{k}` (fix the test, or add it to the red exemption file if the behavior already existed)")
            items += 1
    fl = I["flaky"]
    if fl:
        for f in fl.get("failing", []):
            a(f"- Failing test `{f['key']}`: decide if the test or the product is wrong")
            items += 1
    if not items:
        a("- None")
    a("")
    rnd, low = audit_sample(cfg, feature, sc, iteration)
    a("## 9. Human audit sample")
    a("")
    a("Read only these tests. Record your verdict (accept / revise / reject) in "
      f"`{rel(feature.runs / 'human-audit.json')}`. Then run `qestack calibrate`.")
    a("")
    for k in rnd:
        a(f"- [random] `{k}`")
    for k in low:
        a(f"- [lowest judge score] `{k}`")
    a("")
    return "\n".join(L) + "\n"


def cmd_score(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    sc = compute_score(cfg, feature, getattr(args, "ci", False))
    it = args.iteration or 1
    if getattr(args, "ci", False):
        decision = "ACCEPT" if sc["accepted"] else "FAIL"
        reason = ("all hard gates pass and TQS meets the minimum" if sc["accepted"]
                  else "CI check failed: " + (", ".join(sc["hard_gate_failures"]) or f"TQS below {sc['tqs_min']}"))
        hist = []
        hp = feature.runs / "history.jsonl"
        if hp.exists():
            hist = [json.loads(x) for x in hp.read_text().splitlines() if x.strip()]
    else:
        decision, reason, hist = decide(cfg, feature, sc, it)
    sc_out = {k: v for k, v in sc.items() if k not in ("inputs", "judge")}
    sc_out.update(decision=decision, reason=reason, iteration=it)
    if sc["judge"]:
        sc_out["judge_summary"] = {
            "reviewed": len(sc["judge"]["tests"]), "unreviewed": len(sc["judge"]["unreviewed"]),
            "invalid": len(sc["judge"]["invalid"]),
            "verdicts": {v: sum(1 for t in sc["judge"]["tests"].values() if t["verdict"] == v) for v in ("accept", "revise", "reject")},
        }
    write_json(feature.runs / "scorecard.json", sc_out)
    report = render_report(cfg, feature, sc, decision, reason, hist, it)
    (feature.runs / "quality-report.md").write_text(report, encoding="utf-8")
    if feature.dir.exists():
        (feature.dir / "quality-report.md").write_text(report, encoding="utf-8")
    print(f"score: TQS={sc['tqs']} (min {sc['tqs_min']}){' partial' if sc['tqs_partial'] else ''} | "
          f"hard gate failures: {', '.join(sc['hard_gate_failures']) or 'none'} | decision: {decision}")
    print(f"report: {rel(feature.dir / 'quality-report.md')}")
    return {"ACCEPT": 0, "CONTINUE": 1, "FAIL": 1, "ESCALATE": 3}[decision]


def mutated_line(path: str, line: int) -> str:
    """The one source line of a surviving mutant, so that the writer does not open the production file."""
    p = ROOT / path
    if not line or not p.is_file():
        return ""
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[line - 1].strip()[:200].replace("`", "'") if line <= len(lines) else ""


def cmd_feedback(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    sc = compute_score(cfg, feature)
    I = sc["inputs"]
    it = args.iteration or 1
    N = cfg.get_path("loop.max_feedback_mutants", 40)
    L = []
    a = L.append
    a(f"# Test improvement feedback: {feature.name}, iteration {it}")
    a("")
    a(f"Current TQS: {sc['tqs']} (minimum {sc['tqs_min']}). Failing gates: {', '.join(sc['hard_gate_failures']) or 'none'}.")
    a("")
    a("Rules: Strengthen or add tests. Do not remove tests, assertions or requirement tags. Do not add skips. "
      "Do not change an expected value to match the code. If the code is wrong, log it in "
      f"`{rel(feature.runs / 'suspected-bugs.md')}`.")
    a("")
    lint = I["lint"]
    if lint:
        bad = [t for t in lint["tests"] if t["classification"] != "OK" or t["skipped"] or t["todo"] or not t["ids"] or not t["categories"] or t["smells"]]
        if bad:
            a("## A. Static problems (fix all)")
            a("")
            for t in bad:
                probs = ([t["classification"]] if t["classification"] != "OK" else []) + (["SKIPPED"] if t["skipped"] else []) + \
                        (["TODO"] if t["todo"] else []) + (["NO REQUIREMENT TAG"] if not t["ids"] else []) + \
                        (["NO CATEGORY TAG"] if not t["categories"] else []) + [f"smell:{s}" for s in t["smells"]]
                a(f"- `{t['file']}:{t['line']}` {t['class']}.{t['method']}: {', '.join(probs)}")
            a("")
    tr = I["trace"]
    if tr:
        gaps = [r for r in tr["requirements"] if not r["depth_ok"]]
        if gaps or tr["unknown_ids"]:
            a("## B. Requirement gaps")
            a("")
            for r in gaps:
                what = "no test" if not r["covered"] else "missing categories: " + ", ".join(r["missing_categories"])
                a(f"- **{r['id']}** ({what}): {r['text']}")
            for rid in tr["unknown_ids"]:
                a(f"- Unknown ID `{rid}` in tests. Use an ID from spec.md or test-plan.md.")
            a("")
    m = I["mutation"]
    if m and m.get("survivors"):
        a("## C. Surviving mutants (each needs a test that fails on this change)")
        a("")
        for s in m["survivors"][:N]:
            a(f"- `{s['file']}:{s['line']}` {s['mutator']}: {s['description']}" + (" (no test executes this line)" if s["status"] == "no_coverage" else ""))
            src = mutated_line(s["file"], s["line"])
            if src:
                a(f"  - method `{s.get('method') or '?'}`, line: `{src}`")
        if len(m["survivors"]) > N:
            a(f"- ... {len(m['survivors']) - N} more")
        a("")
    sf = read_json(feature.runs / "seed-feedback.json")
    if sf:
        und = [f for f in sf["faults"] if f["status"] == "UNDETECTED"]
        if und:
            a("## D. Undetected realistic faults (details are hidden on purpose)")
            a("")
            for f in und:
                a(f"- A fault in **{f.get('req_id') or 'unknown requirement'}** (layer: {f.get('layer') or 'unknown'}) was not detected. "
                  "Check all observable effects of this requirement: values, state, events, errors.")
            a("")
    fl = I["flaky"]
    if fl and (fl["flaky"] or fl["failing"]):
        a("## E. Reliability")
        a("")
        for f in fl["flaky"]:
            a(f"- FLAKY `{f['key']}` {f['history']}: remove order dependence, shared data, timing assumptions")
        for f in fl["failing"]:
            a(f"- FAILING `{f['key']}`: compare the test with the spec. If the test is right, log a suspected bug. Do not change the oracle.")
        a("")
    g = I["guard"]
    if g and g["violations"]:
        a("## F. Guard violations (undo these)")
        a("")
        for x in g["violations"]:
            a(f"- {x['type']}: `{x['test']}` ({x['detail']})")
        a("")
    j = sc["judge"]
    if j:
        bad = [(k, v) for k, v in j["tests"].items() if v["verdict"] != "accept"]
        if bad or j["raw"].get("requirement_findings"):
            a("## G. Judge findings")
            a("")
            for k, v in bad:
                a(f"- **{v['verdict'].upper()}** `{k}`")
                for f in v.get("findings") or []:
                    a(f"  - [{f.get('dimension', '')}] {f.get('issue', '')} Fix: {f.get('fix', '')} ({f.get('evidence', '')})")
            for f in j["raw"].get("requirement_findings") or []:
                a(f"- Requirement {f.get('id', '')}: {f.get('issue', '')} Fix: {f.get('fix', '')}")
            a("")
    p = feature.runs / f"feedback-{it}.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"feedback: {rel(p)}")
    return 0


def cmd_calibrate(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    human = read_json(feature.runs / "human-audit.json", [])
    j = read_json(feature.runs / "judge.json", {})
    if not human or not j:
        die("Need human-audit.json ([{\"key\": ..., \"verdict\": \"accept|revise|reject\"}]) and judge.json.", 1)
    lint = read_json(feature.runs / "lint.json", {}) or {}
    jt = load_judge(feature, lint.get("tests", []))["tests"]
    pairs = [(h["verdict"].lower(), jt[h["key"]]["verdict"]) for h in human if h.get("key") in jt]
    if not pairs:
        die("No overlap between human-audit.json and judge.json keys.", 1)
    cats = ["accept", "revise", "reject"]
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pe = sum((sum(a == c for a, _ in pairs) / n) * (sum(b == c for _, b in pairs) / n) for c in cats)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    res = {"feature": feature.name, "created": now_iso(), "n": n, "agreement": round(po, 4), "kappa": round(kappa, 4),
           "disagreements": [{"key": h["key"], "human": h["verdict"], "judge": jt[h["key"]]["verdict"]}
                             for h in human if h.get("key") in jt and h["verdict"].lower() != jt[h["key"]]["verdict"]]}
    write_json(feature.runs / "calibration.json", res)
    hist = ROOT / cfg.get_path("paths.runs_dir", ".qestack/runs") / "calibration-history.jsonl"
    with open(hist, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({k: res[k] for k in ("feature", "created", "n", "agreement", "kappa")}) + "\n")
    print(f"calibrate: n={n} agreement={po:.0%} kappa={kappa:.2f} "
          + ("(trust the judge)" if kappa >= 0.7 else "(do not trust judge scores yet; fix the rubric or prompt)"))
    return 0 if kappa >= 0.6 else 1



# --------------------------------------------------------------------------------------
# fault (helpers for the fault seeder agent: build patches against the CURRENT files)
# --------------------------------------------------------------------------------------


LAYERS = ["domain", "api", "db", "kafka", "ui"]


def cmd_fault(args, cfg):
    import difflib
    import shutil
    feature = resolve_feature(cfg, args.feature, strict=True)
    fdir = feature.runs / "faults"
    base = fdir / ".base"
    manifest = base / ".manifest.json"
    recover_applied_fault(fdir)

    def diff_against_base():
        known = set(read_json(manifest, []) or [])
        out = []
        for f in sorted(set(find_files(cfg, "source_globs")) | known):
            b, cur_p = base / f, ROOT / f
            old = b.read_text(encoding="utf-8", errors="replace") if f in known and b.exists() else None
            cur = cur_p.read_text(encoding="utf-8", errors="replace") if cur_p.exists() else None
            if cur != old:
                out.append((f, old, cur))
        return out

    if args.action == "begin":
        if manifest.exists() and not args.force:
            dirty = diff_against_base()
            if dirty:
                die("The source code differs from the saved clean copy: " + ", ".join(f for f, _, _ in dirty[:5])
                    + ". A fault may still be in the code. Run 'qestack fault restore' first. "
                      "If the code change is intended, use 'fault begin --force'.", 1)
        if base.exists():
            shutil.rmtree(base)
        files = find_files(cfg, "source_globs")
        for f in files:
            dst = base / f
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / f, dst)
        write_json(manifest, files)
        (fdir / ".gitignore").write_text("*\n")
        print(f"fault begin: {len(files)} source file(s) saved. Edit ONE fault, then run 'fault save'.")
        return 0
    if not manifest.exists():
        die("Run 'qestack fault begin' first.")
    changed = diff_against_base()

    def restore(items):
        for f, old, cur in items:
            if old is None:
                (ROOT / f).unlink(missing_ok=True)
            else:
                (ROOT / f).parent.mkdir(parents=True, exist_ok=True)
                (ROOT / f).write_text(old, encoding="utf-8")

    if args.action == "restore":
        restore(changed)
        print(f"fault restore: {len(changed)} file(s) restored")
        return 0
    if args.action == "save":
        if not changed:
            die("No source change found. Edit the code to inject the fault first.", 1)
        if not args.id or not args.req:
            die("--id and --req are required", 1)
        diff = []
        for f, old, cur in changed:
            a_lines = [] if old is None else (old if old.endswith("\n") else old + "\n").splitlines(True)
            b_lines = [] if cur is None else (cur if cur.endswith("\n") else cur + "\n").splitlines(True)
            diff += difflib.unified_diff(a_lines, b_lines, "/dev/null" if old is None else f"a/{f}",
                                         "/dev/null" if cur is None else f"b/{f}", n=3)
        patch = fdir / f"{args.id}.patch"
        patch.write_text("".join(diff), encoding="utf-8")
        restore(changed)
        chk = git("apply", "--check", str(patch))
        cat_p = fdir / "catalog.json"
        cat = [c for c in (read_json(cat_p, []) or []) if c.get("id") != args.id]
        cat.append({"id": args.id, "req_id": args.req, "layer": args.layer or "", "category": args.category or "",
                    "description": args.desc or "", "files": [c[0] for c in changed]})
        write_json(cat_p, cat)
        print(f"fault save: {rel(patch)} ({len(changed)} file(s)); code restored; "
              + ("patch applies cleanly" if chk.returncode == 0 else "WARNING patch does not apply: " + chk.stderr.strip()))
        return 0 if chk.returncode == 0 else 1
    return 1

# --------------------------------------------------------------------------------------
# gate (run all automatic gates), context, doctor
# --------------------------------------------------------------------------------------


def cmd_gate(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    skip = set((args.skip or "").split(",")) - {""}
    ns = argparse.Namespace(feature=feature.name, all=False, files=None, json=False, max=30, plan_only=False,
                            runs=None, skip_run=False, base=args.base, all_files=False, no_baseline=False,
                            allow_protected=args.allow_protected, source_unchanged=args.source_unchanged)
    steps = [("lint", cmd_lint), ("trace", cmd_trace), ("guard", cmd_guard), ("flaky", cmd_flaky),
             ("mutation", cmd_mutation), ("seed", cmd_seed)]
    rc = {}
    for name, fn in steps:
        if name in skip:
            continue
        if name == "seed" and not list((feature.runs / "faults").glob("*.patch")):
            info("seed: no fault patches; skipped")
            continue
        print(f"\n== {name} ==")
        try:
            rc[name] = fn(ns, cfg)
        except SystemExit as e:
            rc[name] = e.code if isinstance(e.code, int) else 1
        if args.fast and rc[name] and name in ("lint", "trace", "guard"):
            print(f"\nfast mode: stopping after '{name}' failed")
            break
    print("\n== summary ==")
    for k, v in rc.items():
        print(f"  {k:<9} {'PASS' if v == 0 else 'FAIL'}")
    return 0 if all(v == 0 for v in rc.values()) else 1


def data_file(name: str) -> Path | None:
    """Resolve 'guardrails', 'rubrics/test-judge', 'rulesets/kafka', ... (project folder first)."""
    name = name.strip().strip("/")
    if ".." in Path(name).parts:
        return None
    cands = []
    for base in (QE_DIR, DATA_DIR):
        p = base / name
        cands += [p] + [p.with_name(p.name + ext) for ext in (".md", ".toml", ".json", ".yml", ".sh")]
    for c in cands:
        if c.is_file():
            return c
    return None


def docs_for_agents(cfg: Cfg):
    """Guidance files every agent must read, as absolute paths."""
    pr = project_settings().get("project", {})
    out = [str(data_file("guardrails.md"))]
    if pr.get("stack"):
        p = find_layer("stacks", pr["stack"], "md")
        if p:
            out.append(str(p))
    for rs in pr.get("rulesets", []):
        p = find_layer("rulesets", rs, "md")
        if p:
            out.append(str(p))
    rules = ROOT / pr.get("rules_doc", ".qestack/project-rules.md")
    if rules.exists():
        out.append(str(rules))
    return out


def cmd_context(args, cfg):
    feature = resolve_feature(cfg, args.feature)
    d = feature.to_dict()
    pr = project_settings().get("project", {})
    base = resolve_base(cfg, None)
    src_globs, exc = cfg.get_path("paths.source_globs", []), cfg.get_path("paths.exclude_globs", [])
    d.update({
        "engine": {"command": "qestack", "version": TOOL_VERSION, "data_dir": str(DATA_DIR)},
        "base_ref": base or "",
        "changed_source_files": [f for f in changed_files(base) if matches_any(f, src_globs) and not matches_any(f, exc)],
        "stack": pr.get("stack", ""),
        "rulesets": pr.get("rulesets", []),
        "guidance_docs": docs_for_agents(cfg),
        # data_file(): a copy in .qestack/ (for example .qestack/rubrics/test-judge.md) wins over the bundled file
        "rubrics": {"tests": str(data_file("rubrics/test-judge.md")),
                    "plan": str(data_file("rubrics/test-plan.md")),
                    "faults": str(data_file("rubrics/fault-catalog.md"))},
        "templates": {"test_plan": str(data_file("templates/test-plan.md")),
                      "judge_schema": str(data_file("templates/judge-output.schema.json"))},
        "guardrails": str(data_file("guardrails.md")),
        "contracts_dir": rel(feature.dir / "contracts"),
        "data_model": rel(feature.dir / "data-model.md"),
        "test_globs": cfg.get_path("paths.test_globs", []),
        "source_globs": cfg.get_path("paths.source_globs", []),
        "language": cfg.get_path("language.name", ""),
        "tag_examples": cfg.get_path("language.tag_examples", {}),
        "commands": cfg.get("commands", {}),
        "loop": cfg.get("loop", {}),
        "gates": cfg.get("gates", {}),
        "git_head": git_head(),
    })
    print(json.dumps(d, indent=2))
    return 0


def cmd_doctor(args, cfg):
    ok = True

    def chk(cond, good, bad):
        nonlocal ok
        print(("  OK   " if cond else "  FAIL ") + (good if cond else bad))
        ok = ok and cond

    print(f"qestack doctor (engine {TOOL_VERSION})")
    chk(sys.version_info >= (3, 11), f"Python {sys.version.split()[0]}", "Python 3.11+ needed")
    chk(git("--version").returncode == 0, "git found", "git not found")
    proj = QE_DIR / "project.toml"
    chk(proj.exists(), ".qestack/project.toml found", ".qestack/project.toml missing (run 'qestack init')")
    pr = project_settings().get("project", {})
    st = pr.get("stack")
    chk(bool(st) and find_layer("stacks", st, "toml") is not None, f"stack: {st}",
        f"stack '{st}' not found (run 'qestack show stacks')" if st else "no stack set in [project] stack")
    for rs in pr.get("rulesets", []):
        chk(find_layer("rulesets", rs, "md") is not None or find_layer("rulesets", rs, "toml") is not None,
            f"ruleset: {rs}", f"ruleset '{rs}' not found (run 'qestack show rulesets')")
    for c in ("compile", "test_feature", "mutation"):
        chk(bool(cfg.get_path(f"commands.{c}")), f"command '{c}' set", f"command '{c}' is empty")
    chk(bool(cfg.get_path("reports.junit_globs")), "junit report globs set", "reports.junit_globs empty")
    tf = find_files(cfg, "test_globs")
    print(f"  {'OK  ' if tf else 'WARN'} {len(tf)} test file(s) match paths.test_globs"
          + ("" if tf else " (fine before the first test-write phase)"))
    sf = find_files(cfg, "source_globs")
    chk(bool(sf), f"{len(sf)} source file(s) found", "no source files match paths.source_globs")
    tests = scan_all_tests(cfg, tf)
    print(f"  INFO {len(tests)} test method(s) parsed; {sum(bool(t['features']) for t in tests)} with a feature tag; "
          f"{sum(bool(t['ids']) for t in tests)} with requirement IDs")
    specs = ROOT / cfg.get_path("paths.specs_dir", "specs")
    print(f"  {'OK  ' if specs.exists() else 'WARN'} specs folder {rel(specs)}" + ("" if specs.exists() else " not found"))
    rules = ROOT / pr.get("rules_doc", ".qestack/project-rules.md")
    print(f"  {'OK  ' if rules.exists() else 'WARN'} project rules {rel(rules)}" + ("" if rules.exists() else " not found"))
    settings = ROOT / ".claude" / "settings.json"
    if settings.exists() and "qestack hook" in settings.read_text(errors="replace"):
        print("  OK   guard hook in .claude/settings.json")
    else:
        print("  INFO guard hook not in .claude/settings.json (fine if the qestack plugin is installed; it adds the hook)")
    base = resolve_base(cfg, None)
    chk(base is not None, f"base ref: {base}", "no base ref (set [git] base_ref)")
    return 0 if ok else 1


def detect_stack_and_rulesets():
    files = list_repo_files()
    names = {Path(f).name for f in files}
    stack, notes = None, []
    build_text = ""
    for f in files:
        n = Path(f).name
        if n in ("pom.xml", "build.gradle", "build.gradle.kts", "Directory.Packages.props", "package.json") or n.endswith(".csproj"):
            try:
                build_text += (ROOT / f).read_text(encoding="utf-8", errors="replace")[:200000] + "\n"
            except OSError:
                pass
    if "pom.xml" in names:
        stack = "java-maven-junit5"
    elif "build.gradle" in names or "build.gradle.kts" in names:
        stack = "java-maven-junit5"
        notes.append("Gradle found: the Java rules apply, but set Gradle commands in [commands] and [reports].")
    elif any(n.endswith(".csproj") for n in names):
        stack = "dotnet"
    rulesets = []
    low = build_text.lower()
    if re.search(r"spring-boot-starter-web|jakarta\.ws\.rs|httpclient|okhttp|rest-assured|microsoft\.aspnetcore|webapplicationfactory", low):
        rulesets.append("api-http")
    if re.search(r"jdbc|hibernate|spring-boot-starter-data|flyway|liquibase|entityframework|npgsql|testcontainers.*(postgres|mysql|mssql|oracle)", low):
        rulesets.append("database")
    if re.search(r"kafka", low):
        rulesets.append("kafka")
    if re.search(r"playwright", low):
        rulesets.append("ui-playwright")
    return stack, rulesets, notes


def cmd_init(args, cfg_unused=None):
    import shutil
    QE_DIR.mkdir(exist_ok=True)
    proj = QE_DIR / "project.toml"
    if proj.exists() and not args.force:
        print(f"{rel(proj)} already exists. Use --force to overwrite it.")
    else:
        stack, rulesets, notes = detect_stack_and_rulesets()
        if args.stack:
            stack = args.stack
        if args.rulesets is not None:
            rulesets = [r for r in args.rulesets.split(",") if r]
        if not stack:
            stack = "java-maven-junit5"
            notes.append("No build file found. The stack is a guess: check [project] stack.")
        t = (DATA_DIR / "templates" / "project.toml").read_text(encoding="utf-8")
        t = t.replace('stack = "java-maven-junit5"', f'stack = "{stack}"', 1)
        t = re.sub(r'^rulesets = \[.*\]$', "rulesets = [" + ", ".join(f'"{r}"' for r in rulesets) + "]", t, count=1, flags=re.M)
        t = t.replace('name = "my-service"', f'name = "{ROOT.name}"', 1)
        proj.write_text(t, encoding="utf-8")
        print(f"created {rel(proj)}  (stack: {stack}; rulesets: {', '.join(rulesets) or 'none'})")
        for n in notes:
            print(f"  NOTE {n}")
    rules = QE_DIR / "project-rules.md"
    if not rules.exists():
        shutil.copy2(DATA_DIR / "templates" / "project-rules.md", rules)
        print(f"created {rel(rules)}  (fill it in: agents read it)")
    runs = QE_DIR / "runs"
    runs.mkdir(exist_ok=True)
    if not (runs / ".gitignore").exists():
        shutil.copy2(DATA_DIR / "templates" / "runs.gitignore", runs / ".gitignore")
    locks = QE_DIR / "locks"
    locks.mkdir(exist_ok=True)
    if not (locks / "README.md").exists():
        shutil.copy2(DATA_DIR / "templates" / "locks-README.md", locks / "README.md")
    if args.hook:
        install_guard_hook()
    if args.existing:
        apply_existing_codebase_thresholds(proj)
    if args.speckit:
        cmd_dir = ROOT / ".claude" / "commands"
        cmd_dir.mkdir(parents=True, exist_ok=True)
        for src in sorted((DATA_DIR / "adapters" / "speckit" / "commands").glob("*.md")):
            dst = cmd_dir / src.name
            if dst.exists() and not args.force:
                print(f"kept existing {rel(dst)}")
            else:
                shutil.copy2(src, dst)
                print(f"created {rel(dst)}")
        print("speckit: add the principles in 'qestack show adapters/speckit/constitution-addendum' "
              "to .specify/memory/constitution.md")
    preview_lint()
    print("\nNext steps:")
    print("  1. Run 'qestack doctor'. Fix each FAIL.")
    print("  2. In Claude Code, run /qe-setup. It checks the assertion helpers and the build commands.")
    if not args.hook:
        print("  3. No qestack plugin? Run 'qestack init --hook' to add the guard hook to .claude/settings.json.")
    return 0


def install_guard_hook():
    """Merge the guard hook and the qestack permission from the bundled template into .claude/settings.json."""
    tpl = json.loads((DATA_DIR / "templates" / "claude-settings.json").read_text(encoding="utf-8"))
    dst = ROOT / ".claude" / "settings.json"
    cur = read_json(dst, {}) if dst.exists() else {}
    allow = cur.setdefault("permissions", {}).setdefault("allow", [])
    for rule in tpl["permissions"]["allow"]:
        if rule not in allow:
            allow.append(rule)
    pre = cur.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any("qestack hook" in h.get("command", "") for e in pre for h in e.get("hooks", [])):
        print(f"guard hook already in {rel(dst)}")
    else:
        pre.extend(tpl["hooks"]["PreToolUse"])
        print(f"added the guard hook to {rel(dst)}")
    dst.parent.mkdir(exist_ok=True)
    write_json(dst, cur)


def apply_existing_codebase_thresholds(proj: Path):
    """Uncomment the lower start values for an existing codebase in [gates]."""
    t = proj.read_text(encoding="utf-8")
    t2 = re.sub(r"^# (mutation_min = 0\.60)$", r"\1", t, count=1, flags=re.M)
    t2 = re.sub(r"^# (seed_min = 0\.75)$", r"\1", t2, count=1, flags=re.M)
    if t2 != t:
        proj.write_text(t2, encoding="utf-8")
        print("set the start thresholds for an existing codebase: mutation_min = 0.60, seed_min = 0.75. Raise them each sprint.")


def preview_lint():
    """Show what the lint gate sees in the existing tests, so wrong helper detection shows up at once."""
    try:
        cfg = load_config()
        tests = scan_all_tests(cfg, find_files(cfg, "test_globs"))
    except SystemExit:
        return
    if not tests:
        print("\nNo tests found yet (fine before the first test-write phase).")
        return
    s = lint_summary(tests)
    print(f"\nLint preview: {s['total']} test(s), {s['ok']} OK, {s['hollow']} hollow, {s['no_assertion']} without assertion, "
          f"{s['trivial']} trivial, {s['shallow']} shallow.")
    if s["no_assertion"] > max(1, s["total"] // 10):
        print("  Many tests have no assertion. Your tests may use an assertion helper that qestack does not know.")
        print("  /qe-setup registers it, or add a regex to extra_custom_assertion_regexes in .qestack/project.toml.")


def cmd_show(args, cfg_unused=None):
    what = args.what
    kinds = {"stacks": "stacks", "rulesets": "rulesets", "rubrics": "rubrics", "templates": "templates"}
    if not what:
        for k in kinds:
            names = sorted({p.stem for base in (DATA_DIR / k, QE_DIR / k) if base.exists() for p in base.iterdir() if p.is_file()})
            print(f"{k}: {', '.join(names)}")
        print("other: defaults, guardrails, adapters/speckit/constitution-addendum")
        print("\nUse 'qestack show <kind>/<name>', for example 'qestack show rubrics/test-judge'.")
        return 0
    if what in kinds:
        names = sorted({p.stem for base in (DATA_DIR / what, QE_DIR / what) if base.exists() for p in base.iterdir() if p.is_file()})
        print("\n".join(names))
        return 0
    p = data_file(what)
    if p is None:
        die(f"Nothing found for '{what}'. Run 'qestack show' to list the files.", 1)
    if args.path:
        print(p)
    else:
        sys.stdout.write(p.read_text(encoding="utf-8"))
    return 0


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(prog="qestack", description="qestack: AI test quality gates")
    ap.add_argument("--version", action="version", version=TOOL_VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def feat(p):
        p.add_argument("--feature", "-f", default=None, help="speckit feature dir name/number (default: from branch)")
        return p

    p = feat(sub.add_parser("lint", help="static test quality checks"))
    p.add_argument("--all", action="store_true", help="all tests, not only the feature")
    p.add_argument("--files", nargs="*", help="explicit test files")
    p.add_argument("--json", action="store_true")
    p.add_argument("--max", type=int, default=50)
    p = feat(sub.add_parser("trace", help="requirement traceability and depth"))
    p.add_argument("--plan-only", action="store_true", help="check that the test plan covers all requirement IDs")
    p.add_argument("--json", action="store_true")
    p = feat(sub.add_parser("red", help="red-before-green check (run BEFORE implementation)"))
    p.add_argument("--skip-run", action="store_true", help="parse existing reports only")
    p = feat(sub.add_parser("flaky", help="run feature tests N times in random order"))
    p.add_argument("--runs", type=int)
    p = feat(sub.add_parser("mutation", help="mutation testing on changed source files"))
    p.add_argument("--base")
    p.add_argument("--skip-run", action="store_true")
    p.add_argument("--all-files", action="store_true", help="score all mutants in the report")
    p.add_argument("--max", type=int, default=30)
    p = feat(sub.add_parser("seed", help="apply each seeded fault and check detection"))
    p.add_argument("--no-baseline", action="store_true")
    p = feat(sub.add_parser("guard", help="anti-gaming checks"))
    p.add_argument("--base")
    p.add_argument("--allow-protected", action="store_true", help="report protected changes for review instead of failing (CI with CODEOWNERS)")
    p.add_argument("--source-unchanged", action="store_true", help="fail if production code changed since 'snapshot'")
    p.add_argument("--max", type=int, default=30)
    p = feat(sub.add_parser("lock", help="lock the feature tests (monotonic: refuses weakening)"))
    p.add_argument("--force", action="store_true", help="human only: accept weakening")
    p.add_argument("--phase", default="")
    feat(sub.add_parser("snapshot", help="record production source hashes before a test-only phase"))
    p = feat(sub.add_parser("score", help="compute gates, TQS, decision and quality-report.md"))
    p.add_argument("--iteration", type=int, default=1)
    p.add_argument("--ci", action="store_true", help="CI mode: tests changed after the judge review count as unreviewed")
    p = feat(sub.add_parser("feedback", help="write feedback-<n>.md for the test writer"))
    p.add_argument("--iteration", type=int, default=1)
    feat(sub.add_parser("calibrate", help="judge vs human agreement and Cohen's kappa"))
    p = feat(sub.add_parser("gate", help="run lint, trace, guard, flaky, mutation, seed"))
    p.add_argument("--skip", help="comma list of steps to skip")
    p.add_argument("--fast", action="store_true", help="stop when a cheap gate fails")
    p.add_argument("--base")
    p.add_argument("--allow-protected", action="store_true")
    p.add_argument("--source-unchanged", action="store_true")
    feat(sub.add_parser("context", help="print feature paths and settings as JSON (for agents)"))
    feat(sub.add_parser("doctor", help="check the installation"))
    p = feat(sub.add_parser("fault", help="fault seeder helper: begin | save | restore"))
    p.add_argument("action", choices=["begin", "save", "restore"])
    p.add_argument("--id")
    p.add_argument("--req", help="requirement ID the fault breaks")
    p.add_argument("--layer", choices=LAYERS, help="the layer that the fault breaks")
    p.add_argument("--category", help="rule | boundary | validation | state | event | error-handling ...")
    p.add_argument("--desc")
    p.add_argument("--force", action="store_true", help="begin: save the current code as clean, also when it differs from the last saved copy")
    sub.add_parser("hook", help="Claude Code PreToolUse hook (reads JSON on stdin)")
    p = sub.add_parser("init", help="create .qestack/ in this repository")
    p.add_argument("--stack", help="stack name (default: detected)")
    p.add_argument("--rulesets", help="comma list of rulesets (default: detected)")
    p.add_argument("--speckit", action="store_true", help="also add the speckit phase commands")
    p.add_argument("--hook", action="store_true", help="add the guard hook to .claude/settings.json (not needed with the plugin)")
    p.add_argument("--existing", action="store_true", help="existing codebase: start with lower mutation and seed thresholds")
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    p = sub.add_parser("show", help="list or print bundled stacks, rulesets, rubrics, templates")
    p.add_argument("what", nargs="?", help="for example: stacks, rubrics/test-judge, guardrails")
    p.add_argument("--path", action="store_true", help="print the file path, not the content")

    args = ap.parse_args(argv)
    if args.cmd == "hook":
        return cmd_hook(args)
    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "show":
        return cmd_show(args)
    cfg = load_config()
    fn = {
        "lint": cmd_lint, "trace": cmd_trace, "red": cmd_red, "flaky": cmd_flaky, "mutation": cmd_mutation,
        "seed": cmd_seed, "guard": cmd_guard, "lock": cmd_lock, "snapshot": cmd_snapshot, "score": cmd_score,
        "feedback": cmd_feedback, "calibrate": cmd_calibrate, "gate": cmd_gate, "context": cmd_context,
        "doctor": cmd_doctor, "fault": cmd_fault,
    }[args.cmd]
    return fn(args, cfg)


def run():
    """Console entry point."""
    try:
        sys.exit(main() or 0)
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    run()
