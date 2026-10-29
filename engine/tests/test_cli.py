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


def run(cwd, *args, stdin=None, env_extra=None, root=True):
    """root=False: no QESTACK_ROOT, so the engine must find the project root itself."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    env.pop("QESTACK_ROOT", None)
    if root:
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
        r = run(self.repo.dir, "hook", stdin=json.dumps(payload))
        self.assertNotIn("hook error", r.stderr)  # the hook fails open: an error must not look like an allow
        return r

    def weaken(self):
        return {"tool_name": "Edit", "cwd": str(self.repo.dir), "tool_input": {
            "file_path": TEST_FILE, "old_string": '        assertEquals("ORD-400", e.getMessage());\n', "new_string": ""}}

    def test_hook_blocks_flag_abbreviations_and_init_overrides(self):
        for cmd in ("qestack lock --forc", "qestack lock --feature 003 --fo", "cd . && qestack init --existing",
                    "qestack init --force", "QESTACK_X=1 qestack init --exist"):
            r = self.hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
            self.assertEqual(r.returncode, 2, cmd)
        self.assertEqual(self.hook({"tool_name": "Bash", "tool_input": {"command": "qestack lint --all"}}).returncode, 0)
        r = run(self.repo.dir, "lock", "--forc")
        self.assertEqual(r.returncode, 2, r.stderr)  # argparse: no abbreviations
        self.assertIn("unrecognized arguments", r.stderr)

    def test_hook_protects_agent_guidance_and_local_settings(self):
        for path in (".qestack/guardrails.md", ".qestack/templates/judge-output.schema.json",
                     ".qestack/adapters/speckit/x.md", ".claude/settings.local.json"):
            r = self.hook({"tool_name": "Write", "tool_input": {"file_path": path, "content": "x"}})
            self.assertEqual(r.returncode, 2, path)
        r = self.hook({"tool_name": "Write", "tool_input": {"file_path": ".qestack/audit-2026-10-27.md", "content": "x"}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_hook_sees_the_lock_of_a_feature_with_a_dot_in_its_name(self):
        locks = self.repo.dir / ".qestack/locks"
        (locks / f"{FEATURE}.json").rename(locks / "003-v1.2-discount.json")
        self.assertEqual(self.hook(self.weaken()).returncode, 2)

    def test_hook_blocks_test_edits_when_a_lock_cannot_be_read(self):
        lock = self.repo.dir / f".qestack/locks/{FEATURE}.json"
        lock.write_text("{ not json")
        r = self.hook({"tool_name": "Edit", "cwd": str(self.repo.dir), "tool_input": {
            "file_path": TEST_FILE, "old_string": "assertEquals", "new_string": "assertEquals"}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("cannot be read", r.stderr)
        r = self.hook({"tool_name": "Edit", "cwd": str(self.repo.dir), "tool_input": {
            "file_path": PROD_FILE, "old_string": "class", "new_string": "class"}})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(run(self.repo.dir, "lock").returncode, 2)  # no silent re-lock over a broken lock

    def test_hook_blocks_edits_against_a_newer_lock_schema(self):
        lock = self.repo.dir / f".qestack/locks/{FEATURE}.json"
        data = json.loads(lock.read_text())
        self.assertEqual(data["schema"], 1)
        lock.write_text(json.dumps(dict(data, schema=99)))
        self.assertEqual(self.hook(self.weaken()).returncode, 2)
        r = run(self.repo.dir, "guard")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Update the qestack engine", r.stderr)

    def test_hook_checks_multiedit_and_notebookedit(self):
        r = self.hook({"tool_name": "MultiEdit", "tool_input": {"file_path": TEST_FILE, "edits": [
            {"old_string": '        assertEquals("ORD-400", e.getMessage());\n', "new_string": ""}]}})
        self.assertEqual(r.returncode, 2)
        r = self.hook({"tool_name": "NotebookEdit", "tool_input": {"notebook_path": ".qestack/project.toml", "new_source": "x"}})
        self.assertEqual(r.returncode, 2)

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


STUB_IMPL = ('package com.acme.order;\npublic class Discount {\n  public double apply(double total) {\n'
             '    throw new UnsupportedOperationException("FR-001");\n  }\n}\n')


def write_junit(d, cases):
    """cases: {method: inner xml of <testcase>}."""
    (d / "target/surefire-reports").mkdir(parents=True, exist_ok=True)
    body = "".join(f'<testcase classname="com.acme.order.DiscountTest" name="{k}()">{v}</testcase>' for k, v in cases.items())
    (d / "target/surefire-reports/TEST-x.xml").write_text(f"<testsuite>{body}</testsuite>")


class ReviewFixTests(unittest.TestCase):
    """Fixes from the architecture review of release 0.1."""

    def setUp(self):
        self.repo = Repo("GoodDiscountTest.java")
        self.d = self.repo.dir

    def tearDown(self):
        self.repo.close()

    def seed_two_faults(self, second=('"ORD-400"', '"ORD-500"')):
        prod = self.d / PROD_FILE
        impl = prod.read_text()
        run(self.d, "fault", "begin")
        for fid, req, a, b in [("F01", "FR-001", ">= 100.0", "> 100.0"), ("F02", "FR-002", *second)]:
            prod.write_text(impl.replace(a, b))
            r = run(self.d, "fault", "save", "--id", fid, "--req", req, "--layer", "domain", "--desc", f"secret {fid}")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return impl

    def test_report_and_feedback_hide_fault_details_and_holdout(self):
        proj = self.d / ".qestack/project.toml"
        proj.write_text(proj.read_text() + "\n[loop]\nholdout_ratio = 0.5\nholdout_min = 1\n")
        self.seed_two_faults(second=("IllegalArgumentException", "IllegalStateException"))  # the fake runner cannot detect F02
        run(self.d, "seed")
        seed = self.repo.read_json("seed.json")
        self.assertEqual(sum(f["holdout"] for f in seed["faults"]), 1)
        self.assertEqual(seed["summary"]["rate_basis"], "holdout")
        fb = self.repo.read_json("seed-feedback.json")
        self.assertEqual(len(fb["faults"]), 1)
        self.assertNotIn(fb["faults"][0]["id"], [f["id"] for f in seed["faults"] if f["holdout"]])
        run(self.d, "lint")
        run(self.d, "score")
        report = (self.d / f"specs/{FEATURE}/quality-report.md").read_text()
        self.assertNotIn("secret", report)
        self.assertIn("secret", (self.d / RUNS / "faults/undetected.md").read_text())

    def test_fault_begin_refuses_dirty_code_and_new_files_round_trip(self):
        prod = self.d / PROD_FILE
        impl = self.seed_two_faults()
        prod.write_text(impl.replace("0.9", "0.8"))  # a fault left in the code
        r = run(self.d, "fault", "begin")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("fault restore", r.stderr)
        run(self.d, "fault", "restore")
        self.assertEqual(prod.read_text(), impl)
        new = self.d / "src/main/java/com/acme/order/Rounding.java"
        new.write_text("package com.acme.order;\nclass Rounding {}\n")
        r = run(self.d, "fault", "save", "--id", "F03", "--req", "FR-001", "--layer", "domain")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(new.exists())  # restore removes a file that the fault added
        self.assertIn("--- /dev/null", (self.d / RUNS / "faults/F03.patch").read_text())
        r = run(self.d, "fault", "save", "--id", "F04", "--req", "FR-001", "--layer", "database")
        self.assertEqual(r.returncode, 2)  # not a known layer

    def test_seed_reverts_a_fault_left_by_a_killed_run(self):
        prod = self.d / PROD_FILE
        impl = self.seed_two_faults()
        fdir = self.d / RUNS / "faults"
        git(self.d, "apply", str(fdir / "F01.patch"))
        (fdir / ".applied").write_text("F01.patch")
        self.assertNotEqual(prod.read_text(), impl)
        run(self.d, "seed")
        self.assertEqual(prod.read_text(), impl)
        self.assertFalse((fdir / ".applied").exists())

    def test_red_reports_errors_separately(self):
        (self.d / PROD_FILE).write_text(STUB_IMPL)
        write_junit(self.d, {"discountAtThreshold": "<failure/>", "noDiscountBelow": "<error/>",
                             "negativeTotalOnlyNotNull": "<error/>"})
        r = run(self.d, "red", "--skip-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        s = self.repo.read_json("red.json")["summary"]
        self.assertEqual((s["red_by_assertion"], s["red_by_error"], s["rate"]), (1, 2, 1.0))
        proj = self.d / ".qestack/project.toml"
        proj.write_text(proj.read_text() + "\n[gates]\nred_counts_errors = false\n")
        r = run(self.d, "red", "--skip-run")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(self.repo.read_json("red.json")["error_only"]), 2)

    def test_flaky_detects_rerun_passes_and_runtime_skips(self):
        proj = self.d / ".qestack/project.toml"
        runner = self.d / "rerun_runner.py"
        runner.write_text(
            "import pathlib\np = pathlib.Path('target/surefire-reports'); p.mkdir(parents=True, exist_ok=True)\n"
            "(p / 'TEST-x.xml').write_text('<testsuite>"
            "<testcase classname=\"com.acme.order.DiscountTest\" name=\"discountAtThreshold()\"><flakyFailure/></testcase>"
            "<testcase classname=\"com.acme.order.DiscountTest\" name=\"noDiscountBelow()\"><skipped/></testcase>"
            "<testcase classname=\"com.acme.order.DiscountTest\" name=\"negativeTotalOnlyNotNull()\"/></testsuite>')\n")
        proj.write_text(proj.read_text().replace('test_feature_random = "python3 fake_runner.py"',
                                                 'test_feature_random = "python3 rerun_runner.py {seed}"'))
        r = run(self.d, "flaky", "--runs", "2")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        fl = self.repo.read_json("flaky.json")
        self.assertEqual([f["key"].split(".")[-1] for f in fl["flaky"]], ["discountAtThreshold"])
        self.assertEqual([f["key"].split(".")[-1] for f in fl["skipped_at_runtime"]], ["noDiscountBelow"])
        self.assertEqual(len(fl["seeds"]), 2)

    def test_shallow_tests_do_not_cover_requirements(self):
        p = self.d / TEST_FILE
        p.write_text(p.read_text().replace('        assertEquals("ORD-400", e.getMessage());\n', ""))
        r = run(self.d, "lint")
        self.assertEqual(r.returncode, 1, r.stdout)
        tests = {t["method"]: t for t in self.repo.read_json("lint.json")["tests"]}
        self.assertEqual(tests["negativeTotalOnlyNotNull"]["classification"], "SHALLOW")
        run(self.d, "trace")
        rows = {x["id"]: x for x in self.repo.read_json("trace.json")["requirements"]}
        self.assertFalse(rows["FR-002"]["covered"])

    def test_hook_protects_results_and_locked_files_in_shell(self):
        run(self.d, "lock")
        def hook(p):
            r = run(self.d, "hook", stdin=json.dumps(p))
            self.assertNotIn("hook error", r.stderr)
            return r
        r = hook({"tool_name": "Write", "tool_input": {"file_path": f"{RUNS}/seed-feedback.json", "content": "{}"}})
        self.assertEqual(r.returncode, 2, r.stderr)
        r = hook({"tool_name": "Write", "tool_input": {"file_path": f"{RUNS}/judge.json", "content": "{}"}})
        self.assertEqual(r.returncode, 0, r.stderr)
        r = hook({"tool_name": "Bash", "tool_input": {"command": f"echo '{{}}' > {RUNS}/red.json"}})
        self.assertEqual(r.returncode, 2, r.stderr)
        r = hook({"tool_name": "Bash", "tool_input": {"command": f"sed -i 's/assertEquals/assertNotNull/' {TEST_FILE}"}})
        self.assertEqual(r.returncode, 2, r.stderr)
        r = hook({"tool_name": "Bash", "tool_input": {"command": f"git diff {TEST_FILE} 2>&1"}})
        self.assertEqual(r.returncode, 0, r.stderr)
        log = self.d / "hook.log"
        run(self.d, "hook", stdin='{"tool_name": "Read", "agent_type": "x"}', env_extra={"QESTACK_HOOK_LOG": str(log)})
        self.assertIn('"agent_type"', log.read_text())

    def test_stub_in_existing_file_needs_review(self):
        run(self.d, "snapshot")
        (self.d / PROD_FILE).write_text((self.d / PROD_FILE).read_text() + "// stub\n")
        (self.d / RUNS / "stubs.json").write_text(json.dumps([PROD_FILE]))
        r = run(self.d, "guard", "--source-unchanged")
        g = self.repo.read_json("guard.json")
        self.assertEqual(g["violations"], [])
        self.assertEqual([x["type"] for x in g["reviews"]], ["STUB_IN_EXISTING_FILE"])

    def test_feedback_shows_mutated_line_and_context_lists_changes(self):
        (self.d / "target/pit-reports").mkdir(parents=True)
        (self.d / "target/pit-reports/mutations.xml").write_text(
            "<mutations><mutation status='SURVIVED'><mutatedClass>com.acme.order.Discount</mutatedClass>"
            "<mutatedMethod>apply</mutatedMethod><lineNumber>5</lineNumber><mutator>a.B</mutator>"
            "<description>boundary</description></mutation></mutations>")
        prod = self.d / PROD_FILE
        prod.write_text(prod.read_text() + "\n")
        run(self.d, "mutation", "--skip-run")
        run(self.d, "feedback")
        fb = (self.d / RUNS / "feedback-1.md").read_text()
        self.assertIn("method `apply`, line: `return total >= 100.0 ? total * 0.9 : total;`", fb)
        (self.d / "src/main/java/com/acme/order/New.java").write_text("class New {}\n")
        ctx = json.loads(run(self.d, "context").stdout)
        self.assertEqual(set(ctx["changed_source_files"]), {PROD_FILE, "src/main/java/com/acme/order/New.java"})
        # A changed file without mutants is listed, because the score ignores it (for example a module that PIT skips).
        r = run(self.d, "mutation", "--skip-run")
        self.assertEqual(self.repo.read_json("mutation.json")["changed_without_mutants"], ["src/main/java/com/acme/order/New.java"])
        self.assertIn("NOTE no mutants for 1 changed file(s): src/main/java/com/acme/order/New.java", r.stdout)
        own = self.d / ".qestack/rubrics/test-judge.md"
        own.parent.mkdir()
        own.write_text("# project rubric\n")
        ctx = json.loads(run(self.d, "context").stdout)
        self.assertEqual(Path(ctx["rubrics"]["tests"]).resolve(), own.resolve())

    def test_mutating_commands_need_an_exact_feature(self):
        git(self.d, "checkout", "-q", "-b", "other-work")
        r = run(self.d, "lock")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--feature", r.stderr)
        self.assertEqual(run(self.d, "lock", "--feature", "003").returncode, 0)
        self.assertEqual(run(self.d, "lint").returncode, 0)  # read-only commands still use the newest feature

    def test_judge_needs_assertion_depth_and_real_evidence(self):
        run(self.d, "lint")
        tests = []
        for t in self.repo.read_json("lint.json")["tests"]:
            sc = {f"R{i}": {"score": 4, "evidence": f"DiscountTest.java:{t['line']}"} for i in range(1, 8)}
            if t["method"] == "noDiscountBelow":
                sc["R3"] = {"score": 2, "evidence": "DiscountTest.java:20"}
            if t["method"] == "discountAtThreshold":
                sc["R2"] = {"score": 4, "evidence": "#looks-fine"}
            tests.append({"key": t["key"], "verdict": "accept", "scores": sc})
        (self.d / RUNS / "judge.json").write_text(json.dumps({"feature": FEATURE, "mode": "test-review", "iteration": 1, "tests": tests}))
        run(self.d, "score")
        js = self.repo.read_json("scorecard.json")["judge_summary"]
        self.assertEqual(js["verdicts"]["revise"], 1)
        self.assertEqual(js["invalid"], 1)


def judge_payload(lint, verdict="accept"):
    return {"feature": FEATURE, "mode": "test-review", "iteration": 1, "tests": [
        {"key": t["key"], "verdict": verdict,
         "scores": {f"R{i}": {"score": 4, "evidence": f"DiscountTest.java:{t['line']}"} for i in range(1, 8)}}
        for t in lint["tests"]]}


class CalibrateTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo("GoodDiscountTest.java")
        self.d = self.repo.dir
        run(self.d, "lint")
        self.keys = [t["key"] for t in self.repo.read_json("lint.json")["tests"]]
        (self.d / RUNS / "judge.json").write_text(json.dumps(judge_payload(self.repo.read_json("lint.json"))))

    def tearDown(self):
        self.repo.close()

    def audit(self, verdicts):
        (self.d / RUNS / "human-audit.json").write_text(json.dumps([{"key": k, "verdict": v} for k, v in verdicts]))
        return run(self.d, "calibrate")

    def test_full_agreement_on_one_label_is_kappa_one(self):
        r = self.audit([(k, "accept") for k in self.keys])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        c = self.repo.read_json("calibration.json")
        self.assertEqual((c["n"], c["agreement"], c["kappa"]), (len(self.keys), 1.0, 1.0))

    def test_agreement_at_chance_level_fails(self):
        # The judge accepts all; the human rejects one. Observed agreement = expected agreement, so kappa = 0.
        r = self.audit([(self.keys[0], "reject")] + [(k, "accept") for k in self.keys[1:]])
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        c = self.repo.read_json("calibration.json")
        self.assertEqual(c["kappa"], 0.0)
        self.assertEqual(c["agreement"], round((len(self.keys) - 1) / len(self.keys), 4))
        self.assertEqual([x["key"] for x in c["disagreements"]], [self.keys[0]])
        hist = (self.d / ".qestack/runs/calibration-history.jsonl").read_text().splitlines()
        self.assertEqual(len(hist), 1)

    def test_no_overlap_is_an_error(self):
        r = self.audit([("unknown::key", "accept")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("No overlap", r.stderr)


class GateTests(unittest.TestCase):
    def test_fast_mode_stops_after_a_failed_cheap_gate(self):
        repo = Repo("WeakDiscountTest.java")
        try:
            r = run(repo.dir, "gate", "--fast")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("fast mode: stopping after 'lint' failed", r.stdout)
            self.assertNotIn("== mutation ==", r.stdout)
            self.assertIn("lint      FAIL", r.stdout)
        finally:
            repo.close()

    def test_skip_and_seed_without_patches(self):
        repo = Repo("GoodDiscountTest.java")
        try:
            r = run(repo.dir, "gate", "--skip", "mutation,flaky", "--base", "main")
            summary = r.stdout.split("== summary ==")[1]
            self.assertEqual([ln.split()[0] for ln in summary.strip().splitlines()], ["lint", "trace", "guard"])
            self.assertIn("seed: no fault patches; skipped", r.stdout + r.stderr)
            self.assertEqual(r.returncode, 0 if "FAIL" not in summary else 1)
        finally:
            repo.close()


class MonorepoHookTests(unittest.TestCase):
    def test_hook_started_at_the_git_root_guards_a_sub_project(self):
        d = Path(tempfile.mkdtemp())
        try:
            git(d, "init", "-q", "-b", "main")
            (d / "svc/.qestack").mkdir(parents=True)
            (d / "svc/.qestack/project.toml").write_text(PROJECT_TOML)
            target = d / "svc/.qestack/project.toml"
            r = run(d, "hook", root=False, stdin=json.dumps(
                {"tool_name": "Write", "cwd": str(d), "tool_input": {"file_path": str(target), "content": "x"}}))
            self.assertEqual(r.returncode, 2, r.stderr)
            r = run(d, "hook", root=False, stdin=json.dumps(
                {"tool_name": "Write", "cwd": str(d), "tool_input": {"file_path": str(d / "README.md"), "content": "x"}}))
            self.assertEqual(r.returncode, 0, r.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class FillTests(unittest.TestCase):
    def test_placeholders_are_shell_quoted(self):
        r = subprocess.run([sys.executable, "-c",
                            "from qestack.cli import fill; print(fill('x {a} {changed_files} {e}', "
                            "{'a': 'com.acme.Foo*', 'changed_files': \"'a b'\", 'e': ''}))"],
                           env=dict(os.environ, PYTHONPATH=str(SRC)), capture_output=True, text=True)
        self.assertEqual(r.stdout.rstrip("\n"), "x 'com.acme.Foo*' 'a b' ", r.stderr)

    def test_empty_build_property_is_left_out(self):
        code = ("import json, sys, tomllib; from qestack.cli import fill; "
                "cmd = tomllib.load(open(sys.argv[1], 'rb'))['commands']['mutation']; "
                "print(json.dumps([fill(cmd, {'target_classes': '', 'feature_test_classes': 'a.BTest*'}), "
                "fill(cmd, {'target_classes': 'a.B*', 'feature_test_classes': ''})]))")
        for stack, prop in (("java-gradle-junit5", "-Pqe."), ("java-maven-junit5", "-D")):
            with self.subTest(stack=stack):
                r = subprocess.run([sys.executable, "-c", code, str(SRC / f"qestack/data/stacks/{stack}.toml")],
                                   env=dict(os.environ, PYTHONPATH=str(SRC)), capture_output=True, text=True)
                no_classes, no_tests = json.loads(r.stdout)
                self.assertNotIn(prop + "targetClasses", no_classes)
                self.assertIn(prop + "targetTests='a.BTest*'", no_classes)
                self.assertIn(prop + "targetClasses='a.B*'", no_tests)
                self.assertNotIn(prop + "targetTests", no_tests)
                self.assertNotIn("{", no_classes + no_tests)


class MutationAllFilesTests(unittest.TestCase):
    """qestack mutation runs the configured command; a fake tool records its arguments."""

    def setUp(self):
        self.repo = Repo("GoodDiscountTest.java")
        d = self.d = self.repo.dir
        (d / "fake_pit.py").write_text(
            "import json, pathlib, sys\n"
            "pathlib.Path('args.json').write_text(json.dumps(sys.argv[1:]))\n"
            "out = pathlib.Path('target/pit-reports'); out.mkdir(parents=True, exist_ok=True)\n"
            "(out / 'mutations.xml').write_text(\"<mutations><mutation status='KILLED'><mutatedClass>com.acme.order.Discount\"\n"
            "    \"</mutatedClass><lineNumber>5</lineNumber><mutator>a.M</mutator><description>x</description></mutation></mutations>\")\n")
        proj = d / ".qestack/project.toml"
        proj.write_text(proj.read_text().replace(
            'mutation = "true"',
            'mutation = "python3 fake_pit.py -Pqe.targetClasses={target_classes} -Pqe.targetTests={feature_test_classes}"'))

    def tearDown(self):
        self.repo.close()

    def args(self):
        return json.loads((self.d / "args.json").read_text())

    def test_all_files_leaves_out_the_empty_class_list(self):
        r = run(self.d, "mutation", "--all-files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.args(), ["-Pqe.targetTests=com.acme.order.DiscountTest*"])
        self.assertEqual(self.repo.read_json("mutation.json")["summary"]["total"], 1)

    def test_changed_class_is_still_passed(self):
        prod = self.d / PROD_FILE
        prod.write_text(prod.read_text() + "\n")
        r = run(self.d, "mutation")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.args(), ["-Pqe.targetClasses=com.acme.order.Discount*",
                                       "-Pqe.targetTests=com.acme.order.DiscountTest*"])


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

    def test_init_hook_and_existing_flags(self):
        d = Path(tempfile.mkdtemp())
        try:
            git(d, "init", "-q", "-b", "main")
            (d / "pom.xml").write_text("<project/>")
            (d / ".claude").mkdir()
            (d / ".claude/settings.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}')
            git(d, "add", "-A")
            for _ in range(2):  # a second run must not add the hook again
                r = run(d, "init", "--hook", "--existing")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            cur = json.loads((d / ".claude/settings.json").read_text())
            self.assertIn("Bash(ls:*)", cur["permissions"]["allow"])
            self.assertIn("Bash(qestack:*)", cur["permissions"]["allow"])
            self.assertEqual(len(cur["hooks"]["PreToolUse"]), 1)
            t = (d / ".qestack/project.toml").read_text()
            self.assertIn("\nmutation_min = 0.60", t)
            self.assertIn("\nseed_min = 0.75", t)
        finally:
            shutil.rmtree(d)

    def test_init_writes_the_agents_md_section(self):
        d = Path(tempfile.mkdtemp())
        try:
            git(d, "init", "-q", "-b", "main")
            r = run(d, "init")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("created AGENTS.md", r.stdout)
            t = (d / "AGENTS.md").read_text()
            self.assertTrue(t.startswith("<!-- qestack:start"))
            self.assertTrue(t.endswith("<!-- qestack:end -->\n"))
            self.assertIn("Never weaken, skip or delete a locked test", t)
            self.assertIn("qestack guard --feature <feature>", t)
            r = run(d, "init")  # a second run keeps the file as it is
            self.assertIn("kept AGENTS.md", r.stdout)
            self.assertEqual((d / "AGENTS.md").read_text(), t)
        finally:
            shutil.rmtree(d)

    def test_init_keeps_the_text_of_an_existing_agents_md(self):
        d = Path(tempfile.mkdtemp())
        try:
            git(d, "init", "-q", "-b", "main")
            own = "# Team rules\n\nUse tabs.\n"
            (d / "AGENTS.md").write_text(own)
            run(d, "init")
            t = (d / "AGENTS.md").read_text()
            self.assertTrue(t.startswith(own + "\n<!-- qestack:start"), t)
            self.assertEqual(t.count("<!-- qestack:start"), 1)
            # An old qestack section is replaced; the text before and after it stays.
            old = own + "\n<!-- qestack:start -->\nold rules\n<!-- qestack:end -->\n\n## More team rules\n"
            (d / "AGENTS.md").write_text(old)
            r = run(d, "init")
            self.assertIn("updated AGENTS.md", r.stdout)
            t = (d / "AGENTS.md").read_text()
            self.assertNotIn("old rules", t)
            self.assertTrue(t.startswith(own + "\n<!-- qestack:start"))
            self.assertTrue(t.endswith("<!-- qestack:end -->\n\n## More team rules\n"), t)
            self.assertEqual(t.count("<!-- qestack:end -->"), 1)
        finally:
            shutil.rmtree(d)

    def test_init_no_agents_md_flag(self):
        d = Path(tempfile.mkdtemp())
        try:
            git(d, "init", "-q", "-b", "main")
            r = run(d, "init", "--no-agents-md")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((d / "AGENTS.md").exists())
            (d / "AGENTS.md").write_text("# Team rules\n")
            run(d, "init", "--no-agents-md")
            self.assertEqual((d / "AGENTS.md").read_text(), "# Team rules\n")
        finally:
            shutil.rmtree(d)

    def test_java_stack_disables_reruns_in_surefire_and_failsafe(self):
        import tomllib
        cmds = tomllib.loads((SRC / "qestack/data/stacks/java-maven-junit5.toml").read_text())["commands"]
        for name in ("test_feature", "test_feature_random"):
            self.assertIn("-Dsurefire.rerunFailingTestsCount=0", cmds[name])
            self.assertIn("-Dfailsafe.rerunFailingTestsCount=0", cmds[name])  # Failsafe has its own name

    def test_gradle_stack_matches_the_maven_stack(self):
        import tomllib
        stacks = SRC / "qestack/data/stacks"
        mvn = tomllib.loads((stacks / "java-maven-junit5.toml").read_text())
        gr = tomllib.loads((stacks / "java-gradle-junit5.toml").read_text())
        # Same Java reading rules: only paths, commands and reports differ.
        for key in ("language", "tags", "smells"):
            self.assertEqual(mvn[key], gr[key], key)
        self.assertIn("**/src/test/java/**/*.java", gr["paths"]["test_globs"])
        for name in ("test_feature", "test_feature_random", "mutation"):
            self.assertIn("{feature_tag}" if name != "mutation" else "{target_classes}", gr["commands"][name])
        self.assertIn("{feature_test_classes}", gr["commands"]["mutation"])
        self.assertIn("{seed}", gr["commands"]["test_feature_random"])
        self.assertTrue(gr["reports"]["mutation_path"].endswith("build/reports/pitest/mutations.xml"))

    def test_init_detects_gradle(self):
        for build_file in ("build.gradle", "build.gradle.kts"):
            d = Path(tempfile.mkdtemp())
            try:
                git(d, "init", "-q")
                (d / build_file).write_text("plugins { java }\n")
                r = run(d, "init")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn('stack = "java-gradle-junit5"', (d / ".qestack/project.toml").read_text())
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
            r = run(d, "show", "../../../etc/passwd")
            self.assertEqual(r.returncode, 1)
        finally:
            shutil.rmtree(d)


class SubProjectTests(unittest.TestCase):
    """A project in a subfolder of a git repository (a monorepo), run without QESTACK_ROOT."""

    def setUp(self):
        self.top = Path(tempfile.mkdtemp(prefix="qestack-mono-"))
        top, svc = self.top, self.top / "svc"
        git(top, "init", "-q", "-b", "main")
        git(top, "config", "user.email", "test@example.com")
        git(top, "config", "user.name", "test")
        (svc / ".qestack").mkdir(parents=True)
        (svc / ".qestack" / "project.toml").write_text(PROJECT_TOML)
        (svc / f"specs/{FEATURE}").mkdir(parents=True)
        shutil.copy(FIX / "spec.md", svc / f"specs/{FEATURE}/spec.md")
        (svc / PROD_FILE).parent.mkdir(parents=True)
        shutil.copy(FIX / "java" / "Discount.java", svc / PROD_FILE)
        (svc / TEST_FILE).parent.mkdir(parents=True)
        shutil.copy(FIX / "java" / "GoodDiscountTest.java", svc / TEST_FILE)
        shutil.copy(FIX / "fake_runner.py", svc / "fake_runner.py")
        (top / "other/src/main/java").mkdir(parents=True)
        (top / "other/src/main/java/Other.java").write_text("class Other {}\n")
        git(top, "add", "-A")
        git(top, "commit", "-qm", "init")
        git(top, "checkout", "-q", "-b", FEATURE)
        self.svc = svc

    def tearDown(self):
        shutil.rmtree(self.top, ignore_errors=True)

    def test_finds_the_root_and_reports_paths_from_it(self):
        p = self.svc / PROD_FILE
        p.write_text(p.read_text() + "\n// changed\n")
        (self.top / "other/src/main/java/Other.java").write_text("class Other { int x; }\n")
        r = run(self.svc / "src" / "main", "context", "--feature", FEATURE, root=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["changed_source_files"], [PROD_FILE])

    def test_guard_reads_the_base_version_from_a_subfolder(self):
        r = run(self.svc, "lock", root=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        p = self.svc / TEST_FILE
        p.write_text(p.read_text().replace('        assertEquals("ORD-400", e.getMessage());\n', ""))
        r = run(self.svc, "guard", root=False)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        guard = json.loads((self.svc / RUNS / "guard.json").read_text())
        self.assertIn("ASSERTIONS_REDUCED", {v["type"] for v in guard["violations"]})

    def test_init_in_a_sub_project_creates_its_own_folder(self):
        sub = self.top / "billing"
        sub.mkdir()
        (sub / "pom.xml").write_text("<project/>")
        r = run(sub, "init", root=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((sub / ".qestack/project.toml").exists())
        self.assertFalse((self.top / ".qestack").exists())


if __name__ == "__main__":
    unittest.main()
