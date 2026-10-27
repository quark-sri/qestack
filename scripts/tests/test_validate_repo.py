"""Tests for the Agent Skills spec check of scripts/validate_repo.py (the --spec mode).

Each case writes one skill folder to a temporary folder and runs the validator on it in a subprocess.

    python -m unittest discover -s scripts/tests -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VALIDATOR = Path(__file__).resolve().parent.parent / "validate_repo.py"
GOOD_DESC = "Finds edge cases for a feature. Use when the user asks 'what edge cases am I missing'."


class SpecCheck(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="qestack-spec-"))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def spec(self, folder, frontmatter):
        d = self.dir / folder
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n# Skill\n", encoding="utf-8")
        return subprocess.run([sys.executable, str(VALIDATOR), "--spec", str(d)], capture_output=True, text=True)

    def assert_fails(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(message, result.stdout)

    def test_spec_clean_skill_passes(self):
        r = self.spec("edge-cases", f'name: edge-cases\ndescription: "{GOOD_DESC}"\nlicense: MIT\n'
                                    'compatibility: "Needs git."\nmetadata:\n  author: quark-sri\n  version: "0.1.0"')
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("errors: 0", r.stdout)

    def test_double_hyphen_in_name_fails(self):
        r = self.spec("edge--cases", f'name: edge--cases\ndescription: "{GOOD_DESC}"')
        self.assert_fails(r, "name 'edge--cases' must be 1-64 lowercase letters")

    def test_capital_letter_in_name_fails(self):
        r = self.spec("Edge-cases", f'name: Edge-cases\ndescription: "{GOOD_DESC}"')
        self.assert_fails(r, "name 'Edge-cases' must be 1-64 lowercase letters")

    def test_name_of_65_characters_fails(self):
        name = "a" * 65
        r = self.spec(name, f'name: {name}\ndescription: "{GOOD_DESC}"')
        self.assert_fails(r, "must be 1-64 lowercase letters")

    def test_name_different_from_folder_fails(self):
        r = self.spec("edge-cases", f'name: edge-case\ndescription: "{GOOD_DESC}"')
        self.assert_fails(r, "name 'edge-case' does not match folder 'edge-cases'")

    def test_description_of_1100_characters_fails(self):
        r = self.spec("edge-cases", f'name: edge-cases\ndescription: "{"x" * 1100}"')
        self.assert_fails(r, "description must have 1-1024 characters")

    def test_description_of_1024_characters_passes(self):
        r = self.spec("edge-cases", f'name: edge-cases\ndescription: "{"x" * 1024}"')
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_missing_description_fails(self):
        r = self.spec("edge-cases", "name: edge-cases")
        self.assert_fails(r, "description must have 1-1024 characters")

    def test_claude_code_field_fails_in_strict_mode(self):
        r = self.spec("edge-cases", f'name: edge-cases\ndescription: "{GOOD_DESC}"\nargument-hint: "[feature]"')
        self.assert_fails(r, "frontmatter key 'argument-hint' is not in the Agent Skills spec")

    def test_compatibility_of_501_characters_fails(self):
        r = self.spec("edge-cases", f'name: edge-cases\ndescription: "{GOOD_DESC}"\ncompatibility: "{"x" * 501}"')
        self.assert_fails(r, "compatibility must have 1-500 characters")

    def test_metadata_that_is_not_a_map_fails(self):
        r = self.spec("edge-cases", f'name: edge-cases\ndescription: "{GOOD_DESC}"\nmetadata: quark-sri')
        self.assert_fails(r, "metadata must be a map")


if __name__ == "__main__":
    unittest.main()
