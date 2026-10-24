# Related projects

Checked in October 2026. The table compares each project with qestack. Each project is good at its own goal; this page only shows the differences.

| Project | Focus | Main difference from qestack |
|---|---|---|
| [Agentic QE](https://github.com/proffesor-for-testing/agentic-qe) (MIT) | A large fleet of QE agents and skills; test generation, coverage gaps, flaky tests, adversarial review | Node.js and TypeScript focus. No requirement traceability gate, no hard pass/fail scorecard, no hidden-fault gate. |
| [qa-skills](https://github.com/petrkindlmann/qa-skills) (MIT) | 50 QA skills; spec-based test generation; AI test review | Playwright, JavaScript and Python focus. No mutation gate, no guard. |
| [claude-qa-automation](https://github.com/ZeroTull/claude-qa-automation) | Java QA agents and skills; framework health audit; agent calibration | Read-only reviewers. No traceability gate, no mutation gate, no improvement loop. |
| [Playwright Test Agents](https://playwright.dev/docs/test-agents) | Planner, generator and healer for UI tests | UI only. No quality metrics. The healer can skip a test when it decides that the feature is broken. qestack forbids this. |
| [TDD Guard](https://github.com/nizos/tdd-guard) (MIT) | Claude Code hook that enforces TDD | Enforces the process only. It does not measure test quality. No Java or .NET reporter listed. |
| [Mutahunter](https://github.com/codeintegrity-ai/mutahunter) (AGPL-3.0) | Mutation testing with LLM-written mutants | One technique only. AGPL license. |
| [Qodo Cover](https://github.com/qodo-ai/qodo-cover) (AGPL-3.0) | Generates tests to raise coverage | Not maintained since June 2025. Optimizes coverage, the metric that qestack does not trust. |

## Research

Meta's paper [Mutation-Guided LLM-based Test Generation at Meta](https://arxiv.org/abs/2501.12862) (ACH) uses the same core idea as the qestack fault seeder: an LLM writes realistic faults, and tests must detect them. The authors report that about half of the fault-detecting tests added no line coverage. This supports the qestack position: coverage is the wrong target. The tool is not public.

## How qestack can work with these projects

- Use Playwright Test Agents to generate UI tests. Use qestack to judge, harden and lock them.
- Use TDD Guard during development. Use the qestack gates before merge.
- Ideas for the qestack roadmap: an LLM equivalent-mutant check (from ACH), failure routing (from claude-qa-automation).
