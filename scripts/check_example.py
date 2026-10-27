#!/usr/bin/env python3
"""Check the gate results of a runnable example against the numbers in its README.

Standard library only. Run the gates first, then:
    python3 scripts/check_example.py examples/order-service-maven --lint-total 5 --mutation 7/15
Exit code 1 if a number differs. CI runs this after the real Maven and Gradle builds.
"""
import argparse
import json
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("example", type=Path)
ap.add_argument("--feature", default="001-order-discount")
ap.add_argument("--lint-total", type=int, required=True, help="number of tests that lint parses")
ap.add_argument("--mutation", required=True, help="killed/total mutants, for example 7/15")
args = ap.parse_args()

runs = args.example / ".qestack" / "runs" / args.feature
errors = []
try:
    lint = json.loads((runs / "lint.json").read_text())["summary"]
    mut = json.loads((runs / "mutation.json").read_text())["summary"]
except (OSError, KeyError, json.JSONDecodeError) as e:
    sys.exit(f"ERROR {args.example}: cannot read the results in {runs}: {e}")
if lint.get("total") != args.lint_total:
    errors.append(f"lint: {lint.get('total')} tests, expected {args.lint_total}")
killed, total = (int(x) for x in args.mutation.split("/"))
if (mut.get("killed"), mut.get("total")) != (killed, total):
    errors.append(f"mutation: {mut.get('killed')} of {mut.get('total')} killed, expected {killed} of {total}")
for e in errors:
    print(f"ERROR {args.example}: {e}")
print(f"{args.example}: lint {lint.get('total')} tests, mutation {mut.get('killed')} of {mut.get('total')} killed")
sys.exit(1 if errors else 0)
