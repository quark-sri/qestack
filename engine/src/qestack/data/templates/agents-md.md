<!-- qestack:start (written by qestack init; qestack init replaces the text between these two lines) -->
## qestack rules

This repository uses qestack to prove that the tests catch bugs. These rules apply to every AI coding agent.

- Never weaken, skip or delete a locked test (see `.qestack/locks/`). If a locked test is wrong, tell the user.
- Never edit the qestack settings (`.qestack/project.toml`, `.qestack/project-rules.md`) or result files (`.qestack/runs/`). Run the qestack command again.
- When you write the tests of a feature, do not read the implementation of that feature.
- Do not judge or review tests that you wrote in the same session. Use a new session.
- Before each commit, run `qestack guard --feature <feature>`. If it fails, fix the cause. Do not change the test to pass it.
- The full rules: `qestack show guardrails`.
<!-- qestack:end -->
