# Contributing to qestack

Thank you for your help. This guide tells you how to contribute.

## Before you start

1. Read the [project plan](docs/PLAN.md) and the [architecture](docs/architecture.md).
2. For a large change, open an issue with the label `proposal` first. Describe the problem and your idea.
3. Write all text in [Simplified Technical English](docs/writing-style.md).

## Set up

```bash
git clone https://github.com/quark-sri/qestack
cd qestack
python3 --version                       # 3.11 or later
python3 -m unittest discover -s engine/tests -v
python3 scripts/validate_repo.py
```

The engine has no dependencies. The tests use the standard library only.

To use your local engine:

```bash
pipx install -e ./engine
```

To use your local plugin in Claude Code:

```
/plugin marketplace add /path/to/qestack
/plugin install qestack@qestack
```

## Types of contribution

| Contribution | Guide |
|---|---|
| A new stack (language, build and test tools) | [docs/guides/adding-a-stack.md](docs/guides/adding-a-stack.md) |
| A new ruleset (rules for one area of testing) | [docs/guides/adding-a-ruleset.md](docs/guides/adding-a-ruleset.md) |
| A new or changed skill or agent | [docs/guides/adding-a-skill.md](docs/guides/adding-a-skill.md) |
| An engine change | Add a test in `engine/tests/`. Keep the engine free of dependencies. |
| Documentation | Use STE. Check the links. |

## Pull requests

1. Make one change in each pull request.
2. Add or update tests.
3. Run `python3 -m unittest discover -s engine/tests` and `python3 scripts/validate_repo.py`.
4. Update `CHANGELOG.md` under "unreleased".
5. Describe what you changed and why. Give the evidence: test output, or a before-and-after report.

## Rules for qestack itself

- Evidence over opinion: a new gate needs a test that shows what it detects.
- Do not weaken a default threshold without a written reason in the pull request.
- Keep result file formats backward compatible. If you must change one, add a `schema` version.
- Do not add a dependency to the engine.

## Code of conduct

This project follows the [code of conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contribution uses the [Apache License 2.0](LICENSE).
