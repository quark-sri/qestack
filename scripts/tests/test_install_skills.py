"""Tests for scripts/install-skills.sh: the installer for agents that read SKILL.md.

Each test runs the script with a temporary HOME and a temporary project, so it never changes a real agent folder.
Set QESTACK_TEST_BASH to run the script with another bash, for example /bin/bash (3.2 on macOS).

    python -m unittest discover -s scripts/tests -v
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
ROOT = SCRIPTS.parent
INSTALL = SCRIPTS / "install-skills.sh"
SOURCE_SKILLS = ROOT / "plugins" / "qestack" / "skills"
BASH = os.environ.get("QESTACK_TEST_BASH", "bash")
NAMES = sorted(d.name for d in SOURCE_SKILLS.iterdir() if (d / "SKILL.md").exists())
LIBRARY = [n for n in NAMES if not (n == "qestack" or n.startswith("qe-"))]


class Installer(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="qestack-install-"))
        self.home = self.tmp / "home"
        self.repo = self.tmp / "repo"
        self.home.mkdir()
        self.repo.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_install(self, *args):
        env = {**os.environ, "HOME": str(self.home)}
        return subprocess.run([BASH, str(INSTALL), *args], capture_output=True, text=True, env=env)

    def installed(self, folder):
        return sorted(p.name for p in folder.iterdir()) if folder.exists() else []

    def test_each_agent_installs_into_its_documented_user_folder(self):
        cases = {
            "claude": [".claude/skills"],
            "codex": [".agents/skills"], "cursor": [".agents/skills"], "copilot": [".agents/skills"],
            "gemini": [".agents/skills"], "devin": [".agents/skills"], "opencode": [".agents/skills"],
            "antigravity": [".gemini/antigravity-cli/skills", ".gemini/config/skills"],
            "cline": [".cline/skills"],
        }
        for agent, folders in cases.items():
            with self.subTest(agent=agent):
                shutil.rmtree(self.home)
                self.home.mkdir()
                r = self.run_install("--agent", agent, "--user")
                self.assertEqual(r.returncode, 0, r.stderr)
                for f in folders:
                    self.assertEqual(self.installed(self.home / f), NAMES, f)
                written = sorted(str(p.relative_to(self.home)) for p in self.home.glob("**/skills"))
                self.assertEqual(written, sorted(folders))

    def test_project_install_uses_the_project_folder(self):
        for agent, folder in {"codex": ".agents/skills", "claude": ".claude/skills", "cline": ".cline/skills"}.items():
            with self.subTest(agent=agent):
                r = self.run_install("--agent", agent, "--project", str(self.repo))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.installed(self.repo / folder), NAMES)
        self.assertEqual(self.installed(self.home), [])

    def test_links_point_to_the_portable_packages(self):
        self.run_install("--agent", "codex", "--user")
        link = self.home / ".agents" / "skills" / "unit-testing"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (ROOT / "dist" / "skills" / "unit-testing").resolve())
        self.assertNotIn("argument-hint", (link / "SKILL.md").read_text())

    def test_copy_writes_real_folders(self):
        r = self.run_install("--agent", "cursor", "--project", str(self.repo), "--copy")
        self.assertEqual(r.returncode, 0, r.stderr)
        skill = self.repo / ".agents" / "skills" / "unit-testing"
        self.assertFalse(skill.is_symlink())
        self.assertTrue((skill / "SKILL.md").is_file())

    def test_library_only_leaves_out_the_gated_skills(self):
        self.run_install("--agent", "codex", "--user", "--library-only")
        self.assertEqual(self.installed(self.home / ".agents" / "skills"), LIBRARY)

    def test_all_installs_each_shared_folder_once_and_leaves_out_claude(self):
        r = self.run_install("--agent", "all", "--user")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count(f"{self.home}/.agents/skills:"), 1)
        self.assertFalse((self.home / ".claude").exists())
        self.assertEqual(self.installed(self.home / ".cline" / "skills"), NAMES)

    def test_a_folder_that_is_not_qestack_is_kept(self):
        own = self.home / ".agents" / "skills" / "unit-testing"
        own.mkdir(parents=True)
        (own / "SKILL.md").write_text("---\nname: unit-testing\ndescription: my own skill\n---\n")
        r = self.run_install("--agent", "codex", "--user")
        self.assertIn("skip unit-testing", r.stdout)
        self.assertEqual((own / "SKILL.md").read_text().splitlines()[2], "description: my own skill")

    def test_a_second_install_replaces_an_earlier_qestack_copy(self):
        self.run_install("--agent", "codex", "--user", "--copy")
        r = self.run_install("--agent", "codex", "--user")
        self.assertNotIn("skip", r.stdout)
        self.assertTrue((self.home / ".agents" / "skills" / "unit-testing").is_symlink())

    def test_unknown_agent_prints_the_list(self):
        r = self.run_install("--agent", "vim", "--user")
        self.assertEqual(r.returncode, 2)
        self.assertIn("unknown agent: 'vim'", r.stderr)
        self.assertIn("codex", r.stderr)

    def test_missing_scope_fails(self):
        r = self.run_install("--agent", "codex")
        self.assertEqual(r.returncode, 2)
        self.assertIn("give --user, or --project", r.stderr)

    def test_missing_project_folder_fails(self):
        r = self.run_install("--agent", "codex", "--project", str(self.tmp / "no-such-repo"))
        self.assertEqual(r.returncode, 2)

    def test_help_lists_the_agents(self):
        r = self.run_install("--help")
        self.assertEqual(r.returncode, 0)
        for agent in ("claude", "codex", "cursor", "copilot", "gemini", "antigravity", "devin", "opencode", "cline"):
            self.assertIn(agent, r.stdout)

    def test_old_form_links_the_source_skills(self):
        target = self.tmp / "skills"
        r = self.run_install(str(target))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.installed(target), NAMES)
        self.assertEqual((target / "unit-testing").resolve(), (SOURCE_SKILLS / "unit-testing").resolve())


if __name__ == "__main__":
    unittest.main()
