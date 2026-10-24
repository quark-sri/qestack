"""End-to-end tests for the qestack command-line tool.

Each test builds a small git repository in a temporary folder and runs the CLI in a
subprocess, the same way a user or an agent runs it. Standard library only:

    python -m unittest discover -s engine/tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
SRC = HERE.parent / "src"
TEST_FILE = "src/test/java/com/acme/order/DiscountTest.java"
PROD_FILE = "src/main/java/com/acme/order/Discount.java"
FEATURE = "003-order-discount"
RUNS = f".qestack/runs/{FEATURE}"

PROJECT_TOML = """
[project]
name = "fixture"
stack = "java-maven-junit5"
rulesets = ["api-http"]

[git]
base_ref = "main"

[language]
extra_custom_assertion_regexes = ['\\bApiAssert\\.\\w+\\s*\\(']

[commands]
compile = "true"
test_feature = "python3 fake_runner.py"
test_feature_random = "python3 fake_runner.py"
mutation = "true"
"""


def run(cwd, *args, stdin=None, env_extra=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    env["QESTACK_ROOT"] = str(cwd)
    for k in ("QESTACK_FEATURE", "GITHUB_HEAD_REF", "SPECIFY_FEATURE", "QESTACK_BASE_REF"):
        env.pop(k, None)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, "-m", "qestack", *args], cwd=cwd, env=env,
                          input=stdin, capture_output=True, text=True)


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class Repo:
    def __init__(self, test_fixture="GoodDiscountTest.java", with_tests=True):
        self.dir = Path(tempfile.mkdtemp(prefix="qestack-test-"))
        d = self.dir
        git(d, "init", "-q", "-b", "main")
        git(d, "config", "user.email", "test@example.com")
        git(d, "config", "user.name", "test")
        (d / ".qestack").mkdir()
        (d / ".qestack" / "project.toml").write_text(PROJECT_TOML)
        (d / f"specs/{FEATURE}").mkdir(parents=True)
        shutil.copy(FIX / "spec.md", d / f"specs/{FEATURE}/spec.md")
        (d / PROD_FILE).parent.mkdir(parents=True)
        shutil.copy(FIX / "java" / "Discount.java", d / PROD_FILE)
        shutil.copy(FIX / "fake_runner.py", d / "fake_runner.py")
        (d / ".gitignore").write_text("target/\n")
        if with_tests:
            (d / TEST_FILE).parent.mkdir(parents=True)
            shutil.copy(FIX / "java" / test_fixture, d / TEST_FILE)
        git(d, "add", "-A")
        git(d, "commit", "-qm", "init")
        git(d, "checkout", "-q", "-b", FEATURE)

    def read_json(self, name):
        return json.loads((self.dir / RUNS / name).read_text())

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class LintTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo("WeakDiscountTest.java")

    def tearDown(self):
        self.repo.close()

    def test_classifies_weak_tests(self):
        r = run(self.repo.dir, "lint")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        tests = {t["method"]: t for t in self.repo.read_json("lint.json")["tests"]}
        self.assertEqual(tests["hollowTest"]["classification"], "HOLLOW")
        self.assertTrue(tests["hollowTest"]["todo"])
        self.assertEqual(tests["noAssertionAtAll"]["classification"], "NO_ASSERTION")
        self.assertEqual(tests["statusOnly"]["classification"], "SHALLOW")
        self.assertEqual(tests["nestedTest"]["classification"], "TRIVIAL")
        self.assertIn("swallowed_exception", tests["nestedTest"]["smells"])
        self.assertIn("FR-002", tests["nestedTest"]["ids"])  # inherited from @Nested class tag
        self.assertTrue(tests["skipped"]["skipped"])
        self.assertEqual(tests["usesHelper"]["classification"], "OK")  # same-file helper asserts
        self.assertIn("fixed_sleep", tests["usesHelper"]["smells"])
        self.assertEqual(tests["customLib"]["classification"], "OK")  # project assertion regex
        self.assertEqual(tests["discountAtThreshold"]["classification"], "OK")

    def test_good_tests_pass(self):
        repo = Repo("GoodDiscountTest.java")
        try:
            r = run(repo.dir, "lint")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        finally:
            repo.close()


class CSharpLintTests(unittest.TestCase):
    def test_csharp(self):
        repo = Repo(with_tests=False)
        try:
            proj = repo.dir / ".qestack" / "project.toml"
            proj.write_text(proj.read_text().replace('stack = "java-maven-junit5"', 'stack = "dotnet"'))
            (repo.dir / "Orders.Tests").mkdir()
            shutil.copy(FIX / "csharp" / "DiscountTests.cs", repo.dir / "Orders.Tests" / "DiscountTests.cs")
            run(repo.dir, "lint")
            tests = {t["method"]: t for t in repo.read_json("lint.json")["tests"]}
            self.assertEqual(tests["Applies_discount"]["classification"], "OK")
            self.assertTrue(tests["Skipped"]["skipped"])
            self.assertEqual(tests["Status_only"]["classification"], "SHALLOW")
            self.assertEqual(tests["Not_null"]["classification"], "TRIVIAL")
            self.assertEqual(tests["Hollow"]["classification"], "HOLLOW")
            self.assertEqual(tests["MsTestStyle"]["classification"], "OK")
        finally:
            repo.close()


class TraceTests(unittest.TestCase):
    def test_scenarios_plan_and_depth(self):
        repo = Repo("GoodDiscountTest.java")
        try:
            (repo.dir / f"specs/{FEATURE}/test-plan.md").write_text(
                "| Req ID | Summary | Test cases | Categories required | Layer |\n"
                "|---|---|---|---|---|\n"
                "| FR-001 | x | TC-001 | positive, boundary | unit |\n"
                "| FR-002 | x | TC-003 | negative, error | unit |\n"
                "| FR-003 | x | - | n/a - open question Q1 | kafka |\n"
                "| EC-01 | x | TC-003 | error | unit |\n"
                "| US1-AS1 | x | TC-001 | positive | unit |\n"
                "| US1-AS2 | x | TC-002 | boundary | unit |\n")
            r = run(repo.dir, "trace", "--plan-only")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = run(repo.dir, "trace")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            t = repo.read_json("trace.json")
            ids = {x["id"] for x in t["requirements"]}
            self.assertEqual(ids, {"FR-001", "FR-002", "US1-AS1", "US1-AS2", "EC-01"})
            self.assertEqual(t["summary"]["coverage"], 1.0)
            self.assertEqual(t["summary"]["depth_ratio"], 1.0)
            self.assertEqual([x["id"] for x in t["excluded_by_plan"]], ["FR-003"])
        finally:
            repo.close()


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo("GoodDiscountTest.java")
        run(self.repo.dir, "lock")

    def tearDown(self):
        self.repo.close()

    def hook(self, payload):
        return run(self.repo.dir, "hook", stdin=json.dumps(payload))

    def test_hook_blocks_weakening_edit(self):
        r = self.hook({"tool_name": "Edit", "cwd": str(self.repo.dir), "tool_input": {
            "file_path": TEST_FILE, "old_string": '        assertEquals("ORD-400", e.getMessage());\n', "new_string": ""}})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("ASSERTIONS_REDUCED", r.stderr)

    def test_hook_allows_strengthening_edit(self):
        old = "        assertEquals(90.0, d.apply(100.0), 0.001);\n"
        r = self.hook({"tool_name": "Edit", "cwd": str(self.repo.dir), "tool_input": {
            "file_path": TEST_FILE, "old_string": old, "new_string": old + "        assertEquals(180.0, d.apply(200.0), 0.001);\n"}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_hook_blocks_protected_files_and_force_lock(self):
        r = self.hook({"tool_name": "Write", "tool_input": {"file_path": ".qestack/project.toml", "content": "x"}})
        self.assertEqual(r.returncode, 2)
        r = self.hook({"tool_name": "Bash", "tool_input": {"command": "sed -i s/a/b/ .qestack/project.toml"}})
        self.assertEqual(r.returncode, 2)
        r = self.hook({"tool_name": "Bash", "tool_input": {"command": "qestack lock --force"}})
        self.assertEqual(r.returncode, 2)
        r = self.hook({"tool_name": "Bash", "tool_input": {"command": "qestack score > /tmp/out.txt"}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_hook_ignores_non_qestack_repos(self):
        plain = Path(tempfile.mkdtemp())
        try:
            r = run(plain, "hook", stdin=json.dumps({"tool_name": "Write", "tool_input": {"file_path": "x.txt"}}))
            self.assertEqual(r.returncode, 0)
        finally:
            shutil.rmtree(plain)

    def test_guard_detects_weakening_against_base(self):
        p = self.repo.dir / TEST_FILE
        p.write_text(p.read_text().replace('        assertEquals("ORD-400", e.getMessage());\n', "")
                     .replace('@Tag("FR-002") ', ""))
        r = run(self.repo.dir, "guard")
        self.assertEqual(r.returncode, 1)
        types = {v["type"] for v in self.repo.read_json("guard.json")["violations"]}
        self.assertTrue({"ASSERTIONS_REDUCED", "TRACE_REMOVED"} <= types, types)

    def test_lock_is_monotonic(self):
        p = self.repo.dir / TEST_FILE
        p.write_text(p.read_text().replace('        assertEquals("ORD-400", e.getMessage());\n', ""))
        r = run(self.repo.dir, "lock")
        self.assertEqual(r.returncode, 1)


class FlowTests(unittest.TestCase):
    """red -> implement -> faults -> seed -> mutation -> judge -> score."""

    def test_full_flow(self):
        repo = Repo("GoodDiscountTest.java")
        d = repo.dir
        try:
            prod = d / PROD_FILE
            impl = prod.read_text()
            prod.write_text('package com.acme.order;\npublic class Discount {\n  public double apply(double total) {\n'
                            '    throw new UnsupportedOperationException("FR-001");\n  }\n}\n')
            r = run(d, "red")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(repo.read_json("red.json")["summary"]["rate"], 1.0)
            prod.write_text(impl)

            run(d, "fault", "begin")
            for fid, req, a, b in [("F01", "FR-001", ">= 100.0", "> 100.0"),
                                   ("F02", "FR-002", '"ORD-400"', '"ORD-500"')]:
                prod.write_text(impl.replace(a, b))
                r = run(d, "fault", "save", "--id", fid, "--req", req, "--layer", "domain")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(prod.read_text(), impl)  # code restored
            r = run(d, "seed")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(repo.read_json("seed.json")["summary"]["rate"], 1.0)
            self.assertNotIn("description", json.dumps(repo.read_json("seed-feedback.json")))
            self.assertEqual(prod.read_text(), impl)

            (d / "target/pit-reports").mkdir(parents=True)
            (d / "target/pit-reports/mutations.xml").write_text(
                "<mutations>"
                "<mutation status='KILLED'><mutatedClass>com.acme.order.Discount</mutatedClass><lineNumber>5</lineNumber><mutator>a.M</mutator><description>x</description></mutation>"
                "<mutation status='SURVIVED'><mutatedClass>com.acme.order.Discount</mutatedClass><lineNumber>4</lineNumber><mutator>a.B</mutator><description>boundary</description></mutation>"
                "</mutations>")
            prod.write_text(impl + "\n")  # a change against main, so mutation has a scope
            r = run(d, "mutation", "--skip-run")
            self.assertEqual(repo.read_json("mutation.json")["summary"]["score"], 0.5)

            run(d, "lint")
            run(d, "trace")
            run(d, "flaky", "--runs", "2")
            run(d, "guard")
            lint = repo.read_json("lint.json")
            judge = {"feature": FEATURE, "mode": "test-review", "iteration": 1, "tests": [
                {"key": t["key"], "verdict": "accept",
                 "scores": {f"R{i}": {"score": 4, "evidence": f"DiscountTest.java:{t['line']}"} for i in range(1, 8)}}
                for t in lint["tests"]]}
            (d / RUNS / "judge.json").write_text(json.dumps(judge))
            r = run(d, "score")
            sc = repo.read_json("scorecard.json")
            gates = {g["gate"]: g["status"] for g in sc["gates"]}
            self.assertEqual(gates["mutation"], "FAIL")  # 50% < 75%
            self.assertEqual(gates["seed"], "PASS")
            self.assertEqual(gates["red"], "PASS")
            self.assertEqual(gates["judge"], "PASS")
            self.assertEqual(sc["decision"], "CONTINUE")
            self.assertTrue((d / f"specs/{FEATURE}/quality-report.md").exists())

            r = run(d, "feedback")
            fb = (d / RUNS / "feedback-1.md").read_text()
            self.assertIn("Discount.java:4", fb)

            # A test changed after the judge review is unreviewed in CI mode.
            p = d / TEST_FILE
            p.write_text(p.read_text().replace("0.001);\n    }\n\n    @Test @Tag(\"FR-001\") @Tag(\"US1-AS2\")",
                                               "0.0001);\n    }\n\n    @Test @Tag(\"FR-001\") @Tag(\"US1-AS2\")"))
            run(d, "lint")
            r = run(d, "score", "--ci")
            sc = repo.read_json("scorecard.json")
            self.assertEqual(sc["decision"], "FAIL")
            jg = [g for g in sc["gates"] if g["gate"] == "judge"][0]
            self.assertEqual(jg["status"], "FAIL")
        finally:
            repo.close()

    def test_judge_rules_reject_missing_evidence(self):
        repo = Repo("GoodDiscountTest.java")
        d = repo.dir
        try:
            run(d, "lint")
            lint = repo.read_json("lint.json")
            tests = []
            for t in lint["tests"]:
                sc = {f"R{i}": {"score": 4, "evidence": f"DiscountTest.java:{t['line']}"} for i in range(1, 8)}
                if t["method"] == "noDiscountBelow":
                    sc["R3"] = {"score": 1, "evidence": "DiscountTest.java:20"}
                if t["method"] == "discountAtThreshold":
                    sc["R2"] = {"score": 4, "evidence": "looks fine"}
                tests.append({"key": t["key"], "verdict": "accept", "scores": sc})
            (d / RUNS / "judge.json").write_text(json.dumps({"feature": FEATURE, "mode": "test-review",
                                                            "iteration": 1, "tests": tests}))
            run(d, "score")
            sc = repo.read_json("scorecard.json")
            self.assertEqual(sc["judge_summary"]["verdicts"]["revise"], 1)  # any score of 1 -> revise
            self.assertEqual(sc["judge_summary"]["invalid"], 1)  # no file:line evidence
        finally:
            repo.close()


class InitShowTests(unittest.TestCase):
    def test_init_detects_stack_and_rulesets(self):
        d = Path(tempfile.mkdtemp())
        try:
            git(d, "init", "-q", "-b", "main")
            (d / "pom.xml").write_text("<project><dependency>spring-boot-starter-web</dependency>"
                                       "<dependency>spring-kafka</dependency><dependency>flyway</dependency></project>")
            git(d, "add", "-A")
            r = run(d, "init", "--speckit")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            t = (d / ".qestack/project.toml").read_text()
            self.assertIn('stack = "java-maven-junit5"', t)
            self.assertIn('rulesets = ["api-http", "database", "kafka"]', t)
            self.assertTrue((d / ".qestack/project-rules.md").exists())
            self.assertTrue((d / ".qestack/runs/.gitignore").exists())
            self.assertTrue((d / ".claude/commands/speckit.testplan.md").exists())
            r = run(d, "doctor")
            self.assertIn("stack: java-maven-junit5", r.stdout)
        finally:
            shutil.rmtree(d)

    def test_show(self):
        d = Path(tempfile.mkdtemp())
        try:
            r = run(d, "show")
            self.assertIn("java-maven-junit5", r.stdout)
            self.assertIn("kafka", r.stdout)
            r = run(d, "show", "rubrics/test-judge")
            self.assertIn("R1. Requirement fidelity", r.stdout)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
