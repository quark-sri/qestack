# Add a ruleset

A ruleset gives the rules for one area of testing, for example HTTP APIs or Kafka. A repository can use many rulesets. Rulesets work with any stack.

## Files

| File | For | Required |
|---|---|---|
| `engine/src/qestack/data/rulesets/<name>.md` | agents | yes |
| `engine/src/qestack/data/rulesets/<name>.toml` | engine | only if the ruleset adds assertion, shallow or smell patterns |

A project can keep a private ruleset in `.qestack/rulesets/`.

## The `.md` guide: required sections

1. **What a complete test checks.** A table of effects and checks. The judge uses it for R3 (assertion depth).
2. **Required cases.** The negative, boundary and error cases that the designer adds to each test plan when they apply.
3. **Rules.** Oracles, isolation, waiting, test data.
4. **Seeded faults for this layer.** Realistic faults for the fault seeder. Use this exact heading.

Use [Simplified Technical English](../writing-style.md). Keep each rule specific enough that a judge can check it.

## The `.toml` file

Use only `extra_` keys, so that the ruleset adds to the stack and does not replace it:

```toml
[language]
extra_assertion_regexes = ['\bmyAssert\s*\(']
extra_shallow_statement_regexes = ['^assertThat\(.*\)\.isVisible\(\)$']

[smells.patterns]
my_smell = 'regex'
```

`[smells.patterns]` entries merge by name. A ruleset entry with the same name as a stack entry replaces it, so keep both patterns in it.

## Steps

1. Write the `.md` guide (and the `.toml` file if needed).
2. Add the name to the detection in `detect_stack_and_rulesets()` in `cli.py`, if a build file can show that the area is used.
3. Add a test if you added patterns.
4. Update the README table and `CHANGELOG.md`.
