---
name: qe-setup
description: Set up qestack AI test quality in a repository. Creates .qestack/, detects the stack and rulesets, registers assertion helpers, checks the build commands and the guard hook. Use when the user installs qestack or changes the stack, or when lint reports false "no assertion" findings.
---

# qe-setup

The settings files (`.qestack/project.toml`, `.qestack/project-rules.md`) are protected. The qestack hook blocks agent edits to them, also through the shell. You propose the text. The user saves the files.

## Steps

1. **Engine.** Run `qestack --version`. If it is missing, give the install command (`pipx install "git+https://github.com/quark-sri/qestack#subdirectory=engine"`) and stop. The version must be 0.1.x, the same as this plugin.
2. **Create the folder.** If `.qestack/project.toml` does not exist, run `qestack init`. Add `--speckit` if `.specify/` exists, and `--existing` if the codebase already has code and tests (lower start thresholds). Read the lint preview at the end of the output: it shows early if an assertion helper is unknown. The command detects the stack and the rulesets. It creates the files once. After that, only the user changes them.
3. **Check the detection.** Read the build files. Compare them with `[project] stack` and `rulesets`. Run `qestack show stacks` and `qestack show rulesets` to see the options. Gradle: use the `java-gradle-junit5` stack, and add the settings from its guide to `build.gradle.kts`.
4. **Assertion helpers.**
   1. Run `qestack lint --all --max 100`.
   2. Open some NO_ASSERTION findings. If a test calls a library method that asserts, that method needs a regex in `extra_custom_assertion_regexes`, in `[language]` of `.qestack/project.toml`. Example: `'\bApiAssert\.\w+\s*\('`.
   3. A helper that checks only the HTTP status is not a strong assertion. Keep it as an entry point and also add it to `extra_shallow_statement_regexes`. The statement text starts at the matched entry point, so `api.assertStatus(201)` is seen as `.assertStatus(201)`. Example: `'^\.assertStatus\w*\('`.
5. **Build commands.** Read the stack guide (`qestack show stacks/<stack>`). Check that the build can run the tests of one tag (Java: `<groups>${qe.groups}</groups>` in Surefire and Failsafe). Check that the mutation tool is set up (PIT for Java). Show the user the missing snippets. Build changes are the user's decision.
6. **Project rules.** Help the user fill in `.qestack/project-rules.md`: system under test, test locations, internal libraries, database and Kafka helpers, test data, exclusions. Give the text. The user saves the file. Use the facts in `.agents/qa-project-context.md` if it exists. If it does not exist, suggest the `qa-project-context` skill: the library skills of this plugin read that file. Do not copy the engine settings into it. `.qestack/project.toml` stays the only place for them.
7. **Thresholds.** For an existing codebase, suggest lower start values (`mutation_min = 0.60`, `seed_min = 0.75`) and a plan to raise them each sprint.
8. **Give the changes to the user.** Show the exact text for each file in one message. Ask the user to save it. Then continue with step 9.
9. **Guard hook.** With the qestack plugin installed, the hook is active. Without the plugin, suggest `qestack init --hook`. It merges the hook and the permission rule into `.claude/settings.json` and keeps the existing entries. For a manual merge, show `qestack show templates/claude-settings`. That template also has an optional permission rule (`Bash(qestack:*)`), so that qestack commands do not ask for approval each time. The user decides about it.
10. **Check the hook.** Try to write one line to `.qestack/project.toml` with the Write tool, with the same content that the file has now. The hook must block it with "[qestack guard] BLOCKED". If the write is not blocked, the guard is not active: check that `qestack` is on the PATH of Claude Code, and tell the user. Do not continue as if the guard works.
11. **Verify.** Run `qestack doctor`. All lines must be OK, or the user accepts each WARN.
12. **Manual check.** Ask the user to run the `test_feature` and `mutation` commands once by hand. Plugin property names can differ between versions (stack guide, section "Check the commands once by hand").
