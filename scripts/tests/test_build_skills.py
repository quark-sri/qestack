"""Tests for scripts/build_skills.py: the portable skill packages.

The build runs once into a temporary folder. Each test checks one property of the output.

    python -m unittest discover -s scripts/tests -v
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILLS = SCRIPTS.parent / "plugins" / "qestack" / "skills"
AGENTS = SCRIPTS.parent / "plugins" / "qestack" / "agents"
BUILD = SCRIPTS / "build_skills.py"
VALIDATOR = SCRIPTS / "validate_repo.py"


def gated(name):
    return name == "qestack" or name.startswith("qe-")


def build(out):
    subprocess.run([sys.executable, str(BUILD), "--out", str(out)], check=True, capture_output=True, text=True)


def body(text):
    return text.split("\n---\n", 1)[1]


class BuildSkills(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = Path(tempfile.mkdtemp(prefix="qestack-build-"))
        build(cls.out)
        cls.names = sorted(d.name for d in SKILLS.iterdir() if (d / "SKILL.md").exists())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out)

    def zip_names(self, path):
        with zipfile.ZipFile(path) as z:
            return z.namelist()

    def test_each_skill_is_built(self):
        self.assertEqual(sorted(d.name for d in (self.out / "skills").iterdir()), self.names)
        self.assertEqual(sorted(z.stem for z in (self.out / "zips").glob("*.zip")), self.names)

    def test_output_passes_the_strict_spec_check(self):
        r = subprocess.run([sys.executable, str(VALIDATOR), "--spec", *map(str, (self.out / "skills").iterdir())],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn(f"spec check: {len(self.names)} skills, errors: 0", r.stdout)

    def test_no_zip_has_argument_hint(self):
        for path in [*(self.out / "zips").glob("*.zip"), *self.out.glob("*.zip")]:
            with zipfile.ZipFile(path) as z:
                for n in z.namelist():
                    if n.endswith("/SKILL.md"):
                        self.assertNotIn("argument-hint", z.read(n).decode(), f"{path.name}: {n}")

    def test_frontmatter_has_license_and_metadata(self):
        text = (self.out / "skills" / "unit-testing" / "SKILL.md").read_text()
        self.assertIn("\nlicense: Apache-2.0\n", text)
        self.assertIn("\nmetadata:\n  author: quark-sri\n", text)
        self.assertIn("\n  source: https://github.com/quark-sri/qestack\n", text)

    def test_gated_skill_keeps_compatibility(self):
        text = (self.out / "skills" / "qe-plan" / "SKILL.md").read_text()
        self.assertIn("\ncompatibility: \"Needs the qestack engine", text)

    def test_body_and_references_are_unchanged(self):
        for name in self.names:
            src, dst = SKILLS / name, self.out / "skills" / name
            self.assertEqual(body((dst / "SKILL.md").read_text()), body((src / "SKILL.md").read_text()), name)
            src_files = sorted(p.relative_to(src) for p in src.rglob("*") if p.is_file() and p.name != "SKILL.md")
            dst_files = sorted(p.relative_to(dst) for p in dst.rglob("*")
                               if p.is_file() and p.name != "SKILL.md" and "personas" not in p.parts)
            self.assertEqual(dst_files, src_files, name)
            for f in src_files:
                self.assertEqual((dst / f).read_bytes(), (src / f).read_bytes(), f"{name}/{f}")

    def test_panel_package_has_each_persona_text_unchanged(self):
        expected = sorted(f for f in AGENTS.glob("*.md") if not f.stem.startswith("qe-"))
        folder = self.out / "skills" / "test-review-panel" / "references" / "personas"
        self.assertEqual(len(expected), 8)
        self.assertEqual(sorted(f.name for f in folder.iterdir()), [f.name for f in expected])
        for f in expected:
            self.assertEqual((folder / f.name).read_bytes(), f.read_bytes(), f.name)

    def test_no_workflow_agent_and_no_other_skill_gets_persona_texts(self):
        self.assertEqual(list((self.out / "skills").glob("*/references/personas/qe-*.md")), [])
        self.assertEqual([p.parent.parent.name for p in (self.out / "skills").glob("*/references/personas")],
                         ["test-review-panel"])

    def test_panel_zip_has_the_persona_texts(self):
        names = self.zip_names(self.out / "zips" / "test-review-panel.zip")
        self.assertIn("test-review-panel/references/personas/saboteur.md", names)
        self.assertEqual(sum("/references/personas/" in n for n in names), 8)

    def test_skill_zip_has_the_skill_folder_as_root(self):
        names = self.zip_names(self.out / "zips" / "unit-testing.zip")
        self.assertIn("unit-testing/SKILL.md", names)
        self.assertTrue(all(n.startswith("unit-testing/") for n in names), names)

    def test_full_bundle_has_all_skills(self):
        roots = {n.split("/", 1)[0] for n in self.zip_names(self.out / "qestack-skills.zip")}
        self.assertEqual(sorted(roots), self.names)

    def test_library_bundle_has_no_gated_skill(self):
        roots = {n.split("/", 1)[0] for n in self.zip_names(self.out / "qestack-qa-library.zip")}
        self.assertEqual(sorted(roots), [n for n in self.names if not gated(n)])

    def test_build_is_reproducible(self):
        def digest(folder):
            return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob("*.zip")}
        first = digest(self.out)
        again = Path(tempfile.mkdtemp(prefix="qestack-build-"))
        try:
            build(again)
            self.assertEqual(digest(again), first)
        finally:
            shutil.rmtree(again)

    def test_rebuild_removes_an_old_skill(self):
        out = Path(tempfile.mkdtemp(prefix="qestack-build-"))
        try:
            (out / "skills" / "old-skill").mkdir(parents=True)
            (out / "zips").mkdir()
            (out / "zips" / "old-skill.zip").write_bytes(b"")
            (out / "keep.txt").write_text("not written by the build")
            build(out)
            self.assertFalse((out / "skills" / "old-skill").exists())
            self.assertFalse((out / "zips" / "old-skill.zip").exists())
            self.assertTrue((out / "keep.txt").exists())
        finally:
            shutil.rmtree(out)


if __name__ == "__main__":
    unittest.main()
