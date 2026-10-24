# Run qestack in CI

CI is the authority for the guard. Agents and hooks can make mistakes; the CI check runs on every pull request.

## What CI runs again, and what it re-uses

| Gate | In CI |
|---|---|
| lint, trace, guard, flakiness, mutation | Run again |
| red | Re-uses the committed `red.json` (the pre-implementation code is gone) |
| seeded faults | Re-uses the committed `seed-feedback.json` (the fault patches are not committed) |
| judge | Re-uses the committed `judge.json`. A test that changed after the review counts as unreviewed (`judge-basis.json`). |

`qestack score --ci` returns 0 only for ACCEPT.

## GitHub Actions

```bash
qestack show templates/ci-github-actions > .github/workflows/qestack.yml
```

## Other CI systems

```bash
qestack show templates/ci > ci/qestack.sh && chmod +x ci/qestack.sh
```

Call `ci/qestack.sh` from your pipeline. Set `QESTACK_FEATURE` if your branch name is not the feature name.

## Protect the settings

```bash
qestack show templates/CODEOWNERS
```

Add these lines to your CODEOWNERS file. Then a human must approve every change to `.qestack/`.

## Install qestack in CI

Before the PyPI release, install from GitHub:

```bash
pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"
```

For a private repository, give the CI job read access to `quark-sri/qestack`.
