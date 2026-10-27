"""In-process tests for the pure rules of the qestack engine.

These tests import qestack.cli and call its functions directly, without a subprocess.
Use this file for table-driven rule cases. Use test_cli.py for command flow and exit codes.

    python -m unittest discover -s engine/tests -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from qestack import cli  # noqa: E402

FIX = HERE / "fixtures"

PROJECT_TOML = """
[project]
name = "rules"
stack = "java-maven-junit5"
"""


class ProjectCase(unittest.TestCase):
    """A temporary qestack project. set_root() points the engine at it."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="qestack-rules-"))
        (self.dir / ".qestack").mkdir()
        (self.dir / ".qestack" / "project.toml").write_text(PROJECT_TOML)
        self.old_root = cli.ROOT
        cli.set_root(self.dir)
        self.cfg = cli.load_config()

    def tearDown(self):
        cli.set_root(self.old_root)
        shutil.rmtree(self.dir, ignore_errors=True)


class ShellRuleTests(ProjectCase):
    def test_shell_commands(self):
        cases = [
            ("qestack lint --all", False),
            ("qestack score > /tmp/out.txt", False),
            ("git diff src/test/java/A.java 2>&1", False),
            ("cat .qestack/project.toml", False),
            ("qestack lock --force", True),
            ("qestack lock --forc", True),
            ("qestack lock --feature 003 --fo", True),
            ("qestack init --existing", True),
            ("cd svc && qestack init --force", True),
            ("echo x > .qestack/project.toml", True),
            ("tee .qestack/project.toml < x", True),
            ("sed -i s/a/b/ .qestack/rubrics/test-judge.md", True),
            ("echo '{}' > .qestack/runs/003-x/red.json", True),
        ]
        for cmd, blocked in cases:
            with self.subTest(cmd=cmd):
                reason = cli.shell_block_reason(self.cfg, cmd, self.dir)
                self.assertEqual(reason is not None, blocked, reason)

    def test_init_is_allowed_before_the_project_exists(self):
        (self.dir / ".qestack" / "project.toml").unlink()
        self.assertIsNone(cli.shell_block_reason(self.cfg, "qestack init --force", self.dir))

    def test_flag_prefixes(self):
        self.assertTrue(cli._has_flag(["--feature", "x", "--forc"], "--force"))
        self.assertTrue(cli._has_flag(["--force=1"], "--force"))
        self.assertFalse(cli._has_flag(["--feature", "003"], "--force"))
        self.assertFalse(cli._has_flag(["-f", "003"], "--force"))


class MutationReportTests(ProjectCase):
    def test_pit_statuses_and_changed_file_filter(self):
        muts = cli.parse_pit(FIX / "mutation" / "pit-mutations.xml", ["src/main/java/com/acme/order/Discount.java"])
        by_line = {m["line"]: m for m in muts}
        self.assertEqual(sorted(by_line), [4, 5, 9, 12])  # RUN_ERROR and the unchanged class are not counted
        self.assertEqual(by_line[5]["status"], "killed")
        self.assertEqual(by_line[9]["status"], "killed")  # TIMED_OUT, inner class maps to the outer file
        self.assertEqual(by_line[4]["status"], "survived")
        self.assertEqual(by_line[12]["status"], "no_coverage")
        self.assertEqual(by_line[4]["mutator"], "ConditionalsBoundaryMutator")
        self.assertEqual(by_line[4]["file"], "src/main/java/com/acme/order/Discount.java")

    def test_stryker_statuses_and_changed_file_filter(self):
        muts = cli.parse_stryker(FIX / "mutation" / "stryker-mutation-report.json", ["src/Orders/Discount.cs"])
        self.assertEqual({m["file"] for m in muts}, {"src/Orders/Discount.cs"})
        self.assertEqual([(m["line"], m["status"]) for m in muts],
                         [(4, "killed"), (5, "killed"), (7, "survived"), (11, "no_coverage")])

    def test_stryker_all_files(self):
        muts = cli.parse_stryker(FIX / "mutation" / "stryker-mutation-report.json", [])
        self.assertEqual(len(muts), 5)


class ConfigAndGlobTests(unittest.TestCase):
    def test_deep_merge(self):
        base = {"a": {"x": 1, "y": 2}, "list": [1], "keep": True}
        out = cli.deep_merge(base, {"a": {"y": 3}, "extra_list": [2], "new": "v"})
        self.assertEqual(out, {"a": {"x": 1, "y": 3}, "list": [1, 2], "keep": True, "new": "v"})
        self.assertEqual(base["a"], {"x": 1, "y": 2})  # the input is not changed

    def test_globs(self):
        cases = [
            ("src/test/java/a/BTest.java", ["src/test/**/*Test.java"], True),
            ("src/test/BTest.java", ["src/test/**/*Test.java"], True),
            ("src/main/java/a/B.java", ["src/test/**/*Test.java"], False),
            (".qestack/templates/x/y.json", [".qestack/templates/**"], True),
            (".qestack/guardrails.md", [".qestack/*.toml"], False),
        ]
        for path, globs, expected in cases:
            with self.subTest(path=path, globs=globs):
                self.assertEqual(cli.matches_any(path, globs), expected)


class ResultSchemaTests(ProjectCase):
    def test_results_carry_a_schema_and_newer_ones_are_refused(self):
        p = self.dir / "r.json"
        cli.write_result(p, {"tool": "x"})
        self.assertEqual(cli.read_result(p)["schema"], cli.RESULT_SCHEMA)
        p.write_text('{"schema": 99}')
        with self.assertRaises(SystemExit):
            cli.read_result(p)
        p.write_text('{"tool": "old"}')  # files from before the schema field are schema 1
        self.assertEqual(cli.read_result(p)["tool"], "old")

    def test_strict_read_and_jsonl(self):
        p = self.dir / "bad.json"
        p.write_text("{ not json")
        self.assertEqual(cli.read_json(p, {}), {})
        with self.assertRaises(cli.InvalidResultFile):
            cli.read_json(p, {}, strict=True)
        h = self.dir / "history.jsonl"
        h.write_text('{"iteration": 1}\nnot json\n\n{"iteration": 2}\n')
        self.assertEqual([x["iteration"] for x in cli.read_jsonl(h)], [1, 2])


if __name__ == "__main__":
    unittest.main()
