---
name: qe-setup
description: Set up qestack in a repository - create .qestack/, detect the stack and rulesets, register the project assertion helpers, check the build commands and verify with qestack doctor. Use when the user installs qestack, adds a repository, changes the stack, or when the lint gate reports false "no assertion" findings.
---

# qe-setup

The settings files are protected. Agents must not change them on their own. Show every proposed change to the user and write it only after a clear "yes".

## Steps

1. **Engine.** Run `qestack --version`. If it is missing, give the install command (`pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"`) and stop.
2. **Create the folder.** If `.qestack/project.toml` does not exist, run `qestack init` (add `--speckit` if the repository uses speckit: `.specify/` exists). The command detects the stack and the rulesets.
3. **Check the detection.** Read the build files. Compare with `[project] stack` and `rulesets`. Run `qestack show stacks` and `qestack show rulesets` to see the options. Gradle: keep the Java stack, and override `[commands]` and `[reports]` with Gradle equivalents.
4. **Assertion helpers.**
   1. Run `qestack lint --all --max 100`.
   2. Open some NO_ASSERTION findings. If a test calls a library method that does assert, that method needs a regex in `extra_custom_assertion_regexes`. Example: `'\bApiAssert\.\w+\s*\('`.
   3. A helper that checks only the HTTP status is not a strong assertion. Keep it as an entry point and also add it to `extra_shallow_statement_regexes`. The statement text starts at the matched entry point, so `api.assertStatus(201)` is seen as `.assertStatus(201)`. Example: `'^\.assertStatus\w*\('`.
5. **Build commands.** Read the stack guide (`qestack show stacks/<stack>`). Check that the build can run the tests of one tag (Java: `<groups>${qe.groups}</groups>` in Surefire and Failsafe). Check that the mutation tool is set up (PIT or Stryker.NET). Show the user the snippets that are missing. Build changes are the user's decision.
6. **Project rules.** Help the user fill in `.qestack/project-rules.md`: system under test, test locations, internal libraries, database and Kafka helpers, test data, exclusions.
7. **Thresholds.** For an existing codebase, suggest lower start values (`mutation_min = 0.60`, `seed_min = 0.75`) and a plan to raise them each sprint.
8. **Show the proposed changes**, get a "yes", then write them. The qestack hook blocks agent edits to these files. If it blocks you, ask the user to apply the change.
9. **Guard hook.** With the qestack plugin installed, the hook is active. Without the plugin, show `qestack show templates/claude-settings` and ask the user to merge it into `.claude/settings.json`.
10. **Verify.** Run `qestack doctor`. All lines must be OK, or the user accepts each WARN.
11. **Manual check.** Ask the user to run the `test_feature` and `mutation` commands once by hand, because plugin property names can differ between versions.
