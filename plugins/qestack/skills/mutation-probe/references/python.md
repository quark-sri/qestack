# Mutation testing recipe: Python

Common choices: `mutmut` or `cosmic-ray`. Check the configuration format for the installed version: it changed between major versions. Use what the project already has.

## mutmut (shape)

1. Configure the paths to mutate and the test command (for example in `setup.cfg` or `pyproject.toml`).
2. Run `mutmut run`.
3. Show the result with `mutmut results`, and one mutant with `mutmut show <id>`.

## Reading the result

- `survived`: the tests passed with the change.
- `killed`: a test failed.
- `timeout` and `suspicious`: check by hand.

## Tips

- Limit the run to the target module; a full run on a large code base takes long.
- Use a fast test selection (`pytest -x -q tests/unit`) as the runner.
