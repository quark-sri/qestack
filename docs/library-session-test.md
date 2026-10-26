# QA library: test in a real Claude Code session

This is the QA library part of HANDOFF Task 4 (task 4a). The validator and CI check the files only. This test checks that the library skills, the personas and the review panel of the qestack plugin work in a real session. It needs no Maven and no engine. Task 4b tests the gated workflow.

Record the results and each problem, with the check ID, in your local task list, not in this file.

## Automated routing checks

The checks S2, S3, S4 and S7 also run as plugin evals, with more cases for neighbor skills. Each case sends a realistic request to a fresh Claude Code session with the plugin loaded. It checks which skill Claude starts, and that the neighbor skill does not start. The cases are in `plugins/qestack/evals/routing/`.

```bash
cd plugins/qestack
claude plugin eval . --tag routing --ablation none --scaffold --no-publish --max-cost-usd 6
```

- `--scaffold` runs the fixture script of the case `library-in-qestack-repo` (our own script: it writes `.qestack/project.toml` and one test class).
- `--no-publish` keeps the report on your machine. Without it, the report is published to claude.ai.
- Each run uses your Claude usage. One run costs about $0.17. The suite has 8 cases with 3 runs each, about $4.

Results of 2026-10-26 (Claude Code default model, 3 runs per case):

| Case | Check | Result |
|---|---|---|
| `review-tests` | S2 | 3 of 3: `testcase-reviewer`, never `test-review-panel` |
| `edge-cases` | S3 | 3 of 3 |
| `where-to-start` | S4 | 3 of 3: `qa-navigator` |
| `library-in-qestack-repo` | S7 | 3 of 3: `testcase-reviewer`, no gated skill |
| `flaky-test` | neighbor | 2 of 3. After 'passes on my machine' went back into the description: 4 of 5. In the other runs, Claude answered the one-snippet question without a skill |
| `bug-report` | neighbor | 3 of 3: `bug-report`, never `bug-hunter` |
| `load-test` | neighbor | 3 of 3 |
| `gated-setup` | gated | 3 of 3 |

The evals do not replace the persona and panel checks (P and R). Those need real files and agents. Run them by hand as below.

## Setup

In Claude Code, from any folder:

```
/plugin marketplace add /Users/srinivas/Documents/repos/qestack
/plugin install qestack@qestack
```

Start a new session in the repository root after the install.

## Targets

| Target | Why | Test command |
|---|---|---|
| `examples/order-discount` | A small test class with weak tests that we planted. The answer key below lists what a reviewer must find. No build file, so no test can run | none |
| `engine/tests` | Real tests that run in seconds. The fault plan of the Saboteur can run here | `python3 -m unittest discover -s engine/tests` |

## Checks

### S: skills

| ID | Do | Pass when |
|---|---|---|
| S1 | Type `/` and look for `qestack:` | The 49 skills are listed: 39 library skills, and `qestack` with the 9 `qe-*` skills |
| S2 | Ask: "review the tests in examples/order-discount" | `testcase-reviewer` starts, not `test-review-panel` |
| S3 | Ask: "what edge cases are missing in examples/order-discount/specs/001-order-discount/spec.md" | `edge-case-hunter` or `requirement-gaps` starts |
| S4 | Ask: "where do I start with testing this repository" | `qa-navigator` starts and proposes at most three skills |
| S5 | In S2 to S4 | Each skill reads `.agents/qa-project-context.md` or suggests `qa-project-context` once, and does not stop |
| S6 | In S2 to S4 | No skill names a tool that the project does not use |
| S7 | In S2 to S4 | The library skill starts, not a gated skill (`qestack`, `qe-*`), although `examples/order-discount` has a `.qestack/` folder. The user did not ask for the gated workflow |

### P: personas

| ID | Do | Pass when |
|---|---|---|
| P1 | Run `/agents` | The 8 personas and the 4 `qe-*` workflow agents are listed |
| P2 | Ask: "use the domain-oracle-reviewer agent on examples/order-discount" | The report starts with the `Persona:` header line and ends with the findings block (valid JSON) |
| P3 | In P2 | Each finding has a file and line. Findings without evidence are under "Questions" |
| P4 | In P2 | The persona changed no file (`git status` is clean) |
| P5 | Ask: "use the saboteur agent on examples/order-discount" | It returns a fault plan with `original` and `mutant` lines, and it does not try to apply a fault |
| P6 | In P5 | Each `original` line occurs exactly once in its file |

### R: review panel

| ID | Do | Pass when |
|---|---|---|
| R1 | Ask: "review the tests in examples/order-discount with the panel" | `test-review-panel` starts, chooses personas and says why |
| R2 | In R1 | The personas start in parallel, as separate agents |
| R3 | In R1 | The panel says that the fault plan cannot run (no build), and does not try to run it |
| R4 | In R1 | One merged, ranked list. Duplicates name all personas that found them |
| R5 | In R1 | It writes `qa-reviews/<date>-<scope>/` with `panel-report.md`, `findings.json` (valid JSON) and `personas/<name>.md` |
| R6 | In R1 | It asks once whether to commit `qa-reviews/` or to ignore it |
| R7 | `/qestack:test-review-panel engine/tests --personas saboteur,hallucination-checker` | The fault plan runs in an isolated copy. `findings.json` has a `fault_plan` result for each fault |
| R8 | After R7 | `git status` shows only `qa-reviews/` (or nothing, if it is ignored). The source files did not change |
| R9 | In R1 and R7 | It offers to publish the report, and does not publish without a yes |

## Answer key for `examples/order-discount`

The panel in R1 must find most of these. The persona in brackets is the expected finder. Line numbers are in `src/test/java/com/acme/order/DiscountTest.java` unless another file is named.

| # | Expected finding | Persona |
|---|---|---|
| K1 | `hollowTest` has no body, only a "to do" comment | ai-behavior-auditor |
| K2 | `negativeTotalOnlyNotNull` checks only that the exception is not null. It does not check the code ORD-400 (FR-002) | ai-behavior-auditor, domain-oracle-reviewer |
| K3 | `noAssertionAtAll` checks nothing | ai-behavior-auditor |
| K4 | `skipped` is disabled as "flaky" with no cause, and `assertEquals(1, 1)` checks nothing | ai-behavior-auditor, determinism-flakiness-engineer |
| K5 | `nestedTest` swallows the exception and asserts `true` | ai-behavior-auditor |
| K6 | `client` in `statusOnly` is not defined | hallucination-checker |
| K7 | `ApiAssert`, `resp`, `x` and `y()` in `customLib` are not defined | hallucination-checker |
| K8 | `FR-099` is not in the spec | hallucination-checker, domain-oracle-reviewer |
| K9 | `statusOnly` checks only the status for FR-003. The event and its key are not checked, and the spec is not clear about the key | domain-oracle-reviewer |
| K10 | `Thread.sleep(100)` in `usesHelper` | determinism-flakiness-engineer |
| K11 | `checkTotal` hides an assertion in a helper with no "assert" in its name | maintainability-craftsperson |
| K12 | A total of 0 has no test. The fault `total < 0` to `total <= 0` survives (`Discount.java`) | saboteur |
| K13 | The error message is not checked. A fault that changes "ORD-400" survives (`Discount.java`) | saboteur |
| K14 | The fault `>=` to `>` is killed by `discountAtThreshold` (a correct prediction of "killed") | saboteur |

Score: the number of K1 to K14 in `panel-report.md`, and the number of findings that are not in the key. Check each extra finding: it is a good find or a false finding.

Report: the result of each check (pass, fail or partial), the number of K1 to K14 found, and the number of extra findings, good and false.
