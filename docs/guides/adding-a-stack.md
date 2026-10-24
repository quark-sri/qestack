# Add a stack

A stack tells qestack how to read the tests of one language and how to run them. Each repository uses exactly one stack.

## Files

| File | For | Content |
|---|---|---|
| `engine/src/qestack/data/stacks/<name>.toml` | engine | file globs, test markers, tag syntax, assertion regexes, smells, commands, report paths |
| `engine/src/qestack/data/stacks/<name>.md` | agents | tag convention, assertion helpers, build setup, mutation tool setup, language rules, stub rules |

A project can also keep a private stack in `.qestack/stacks/<name>.toml` and `.md`.

## Steps

1. Copy `java-maven-junit5.toml` and `.md` as a start.
2. Set `[paths] test_globs` and `source_globs`.
3. Set `[language]`:
   - `string_style`: `java` (Java, Kotlin, TypeScript) or `csharp`. It controls how string literals are masked.
   - `test_marker_regex`: finds the start of each test method (annotation or attribute).
   - `skip_regex`: finds skip markers in the annotation area.
   - `display_name_regex`: one capture group for the display name, if the framework has one.
   - `assertion_regexes`: one regex for each assertion entry point.
   - `trivial_statement_regexes` and `shallow_statement_regexes`: matched against the normalized statement. The statement starts at the assertion entry point. Normalized means: no line breaks, and no spaces around `.`, `(`, `)`, `[`, `]` and `,`.
4. Set `[tags] tag_value_regex`: regexes with one capture group that return each tag value. Tag values are requirement IDs, categories and the feature tag.
5. Set `[smells.patterns]`.
6. Set `[commands]` and `[reports]`. The test command must write JUnit XML. The mutation report must be PIT XML or the Stryker JSON format (the Stryker family uses the open mutation-testing-report schema).
7. Write the `.md` guide. Use the sections of `java-maven-junit5.md`. Use [Simplified Technical English](../writing-style.md).
8. Add a fixture test file with good and weak tests to `engine/tests/fixtures/<language>/`. Add a test to `engine/tests/test_cli.py` that checks each classification: OK, HOLLOW, NO_ASSERTION, TRIVIAL, SHALLOW, skipped, tags.
9. Run `python3 -m unittest discover -s engine/tests`.
10. Update the README table and `CHANGELOG.md`.

## Checklist

- [ ] Each assertion style of the main libraries is recognized.
- [ ] Comments and strings with assertion-like text do not count as assertions.
- [ ] Nested test classes inherit class tags (if the framework supports it).
- [ ] Parameterized tests are found.
- [ ] The feature filter command runs only the tests of one tag.
- [ ] The commands work on Linux CI.
