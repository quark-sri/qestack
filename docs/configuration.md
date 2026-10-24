# Configuration

All project settings are in `.qestack/project.toml`. `qestack init` creates it. This file is protected: agents cannot change it.

## Load order

1. Core defaults (`qestack show defaults`)
2. The stack in `[project] stack`
3. The rulesets in `[project] rulesets`, in the listed order
4. `.qestack/project.toml`

A later level overrides an earlier level. For a list, write `extra_<key>` to append to it instead of replacing it.

## Sections

### `[project]`

| Key | Meaning |
|---|---|
| `name` | Project name for the reports |
| `stack` | Exactly one stack. List: `qestack show stacks` |
| `rulesets` | Zero or more rulesets. List: `qestack show rulesets` |
| `rules_doc` | Project guidance for agents. Default `.qestack/project-rules.md` |

### `[paths]`

| Key | Default | Meaning |
|---|---|---|
| `specs_dir` | `specs` | One folder for each feature, each with `spec.md` |
| `test_globs` | from the stack | Test files |
| `source_globs` | from the stack | Production files |
| `exclude_globs` | build folders | Files to ignore |
| `protected` | `.qestack/` settings and locks | Files that agents must not change |

### `[git]`

| Key | Default | Meaning |
|---|---|---|
| `base_ref` | `origin/main` | Base branch. The engine uses the merge-base. It sets the mutation scope and the guard comparison. |

### `[requirements]`

| Key | Default | Meaning |
|---|---|---|
| `id_regex` | `(?:FR\|NFR\|SC\|AC\|EC\|BR)-\d{2,4}` | Requirement ID pattern |
| `derive_scenario_ids` | `true` | Scenario n of "User Story k" gets the ID `USk-ASn` |
| `required_prefixes` | `FR, US, EC, AC, BR` | IDs that must have tests |
| `feature_tag_format` | `feature-{num}` | The feature tag on test classes |
| `depth_rules.<prefix>` | `FR`: positive + one of negative/boundary/error | Categories needed when the test plan does not list them |

### `[language]`

| Key | Meaning |
|---|---|
| `extra_custom_assertion_regexes` | Assertion entry points of your libraries |
| `extra_shallow_statement_regexes` | Helpers that check only a status or visibility |
| `extra_trivial_statement_regexes` | Assertions that check only existence |

The stack sets the rest (test markers, skip markers, tag syntax).

### `[commands]`

Placeholders: `{feature_tag}`, `{feature}`, `{target_classes}`, `{changed_files}`, `{changed_files_csv}`, `{base_ref}`, `{run}`.

| Key | Meaning |
|---|---|
| `compile` | Compile production and test code |
| `test_feature` | Run the tests of one feature tag and write JUnit XML |
| `test_feature_random` | Same, in random order (flakiness gate) |
| `mutation` | Mutation testing of the changed code |
| `timeout_seconds` | Time limit for each command |

### `[reports]`

| Key | Meaning |
|---|---|
| `junit_globs` | Where the JUnit XML results are |
| `mutation_format` | `pit-xml` or `stryker-json` |
| `mutation_path` | Where the mutation report is |

### `[gates]`

| Key | Default |
|---|---|
| `trace_coverage_min` | 1.0 |
| `hollow_max`, `no_assertion_max`, `skipped_max` | 0 |
| `red_min` | 1.0 |
| `flaky_max`, `failing_max` | 0 |
| `flaky_runs` | 5 |
| `mutation_min` | 0.75 |
| `seed_min` | 0.90 |
| `guard_violations_max`, `judge_rejects_max` | 0 |
| `judge_coverage_min` | 1.0 |
| `tqs_min` | 80 |
| `required` | all gates; a gate in this list fails when its data is missing |

### `[weights]`

`fault_detection` 0.35, `requirement_depth` 0.25, `assertion_strength` 0.15, `independence` 0.15, `maintainability` 0.10.

### `[loop]`

| Key | Default | Meaning |
|---|---|---|
| `max_iterations` | 4 | Then escalate |
| `min_improvement`, `patience` | 2.0, 2 | Escalate when the score does not improve |
| `audit_random`, `audit_lowest` | 5, 5 | Human audit sample size |
| `faults_min`, `faults_max` | 5, 15 | Hidden faults for each feature |

## Human decision files

These files are in `.qestack/locks/`. Only humans change them.

| File | Meaning |
|---|---|
| `<feature>.equivalent.json` | Surviving mutants that cannot change behavior |
| `<feature>.red-exempt.json` | Tests that may pass before the implementation |

## Environment variables

| Variable | Meaning |
|---|---|
| `QESTACK_FEATURE` | Feature name (otherwise from the branch) |
| `QESTACK_BASE_REF` | Base ref (otherwise from `[git] base_ref`) |
| `QESTACK_ROOT` | Repository root (otherwise from git) |
