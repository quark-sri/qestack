# Getting started

This guide takes one feature from spec to an ACCEPT report. It takes about one hour the first time.

## 1. Install

```bash
git clone https://github.com/quark-sri/qestack && qestack/scripts/install.sh
```

The script installs the engine (pipx or uv) and the Claude Code plugins. To do it by hand, see the Install section of the README.

## 2. Set up the repository

```bash
cd your-repo
qestack init --existing   # existing codebase: lower start thresholds. Add --speckit for GitHub Spec Kit.
```

`init` ends with a lint preview of your existing tests. In Claude Code, run `/qe-setup`. It checks the stack, the rulesets, your assertion helpers and the build commands. Then:

```bash
qestack doctor
```

## 3. Write or check the spec

Create `specs/001-<name>/spec.md`. Give each requirement an ID:

```markdown
- **FR-001**: The system MUST apply a 10% discount when the order total is 100.00 or more.
- **FR-002**: The system MUST reject an order with a negative total with error code ORD-400.
```

Run `/qe-grill-spec`. Answer its questions.

## 4. Design, write and prove the tests (before the code)

```
/qe-plan
/qe-write
/qe-prove
```

At the end, the tests fail (the feature does not exist yet) and they are locked.

## 5. Implement the feature

Ask your agent to implement the feature. The hook stops it if it tries to weaken the locked tests.

## 6. Harden

```
/qe-harden
```

Read `specs/001-<name>/quality-report.md`. Review the audit sample. Record your verdicts and run `/qe-calibrate`.

## 7. Commit

Commit the tests, `specs/`, `.qestack/project.toml`, `.qestack/locks/` and the committed files in `.qestack/runs/` (the `.gitignore` there selects them). Add the CI check: see [ci.md](ci.md).
