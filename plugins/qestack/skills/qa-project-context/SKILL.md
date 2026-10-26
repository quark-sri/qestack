---
name: qa-project-context
description: "Create or update .agents/qa-project-context.md, the one file that records the product, tech stack, test stack, test commands, CI, environments, quality goals, risk areas and conventions of a project. Every other QA skill reads it first. Use when: 'set up QA context', 'onboard QA to this repo', 'configure testing', or before the first QA skill in a new repository. Not for: a test strategy (use test-strategy) or a risk matrix (use risk-based-testing). Related: qa-navigator, test-strategy, risk-based-testing, test-runner."
argument-hint: "[create | update | check]"
---

# qa-project-context

## Objective

Without shared context, each QA skill asks again where the tests are, how to run them and what matters most. This skill writes `.agents/qa-project-context.md` once. Each fact in it has a source, or it says "unknown". Other skills then start from facts, not from guesses.

## Context

If `.agents/qa-project-context.md` exists, read it first. Check each section against the repository. Mark the facts that are no longer true.

If `.qestack/project.toml` exists, the repository uses the qestack gated workflow. Read the stack, the test commands and the thresholds from it, with that file as the source. Do not copy its settings. Point to it.

## Discovery questions

Find the answers in the repository first (see the workflow). Ask the user only about gaps that change the work. Ask one section at a time.

1. **Product.** What does the product do, in one sentence? What are the 5 to 10 user journeys that must never break?
2. **Tech stack.** Languages, frameworks, API styles, databases, message brokers, caches, external services.
3. **Test stack.** Test frameworks for each level (unit, API, integration, contract, UI, performance). Where the tests live. How to run all tests, one module, one file, one test, one tag.
4. **CI and delivery.** Which pipeline runs which tests, on which event. What blocks a merge or a deploy. Where the reports go.
5. **Environments.** Local, shared test, staging, production. How close is staging to production? Which services are real and which are simulated?
6. **Quality goals.** Coverage or mutation targets, flaky test policy, test run time budget, release criteria.
7. **Risk areas.** Areas with incidents, high change, complex rules, money, security or personal data.
8. **Conventions.** Test naming, folder layout, tags or groups, test data approach, requirement IDs and where they live.

## Workflow

1. **Scan the repository.** Read the build and dependency files, the test framework configuration, the test folders, the CI configuration, the container and environment files, the README and the contributing guide.
2. **Record the facts** in the template from [the context template](references/template.md). Write the source of each fact (a file path). Write a version only from a lock file or an installed package. A version range in a build file is not the installed version.
3. **Check the test command.** If the user agrees, run the fastest test command once. Record if it worked. A configuration file alone does not prove that the tests run.
4. **Ask** about the gaps that matter, one section at a time.
5. **Write** `.agents/qa-project-context.md`. Show the user the result and the open questions.

## Anti-patterns

- **Invented facts.** A plausible guess in the context file misleads every later skill. Write "unknown" instead.
- **Template left with placeholders.** A file with placeholder text answers nothing. Other skills treat it as absent.
- **A one-time file.** Update the file when the stack, the pipeline or the risks change. Each skill can mark stale facts.

## Done when

- Each section has facts with a source, or an explicit "unknown".
- The test commands are listed for each level, and at least one command was run or is marked "not run".
- The critical user journeys and the risk areas are listed.
- The open questions are listed for the user.

## Related skills

- `qa-navigator`: which QA skill to use next.
- `risk-based-testing`: uses the risk areas.
- `test-strategy`: uses the whole file.
- `test-runner`: uses the test commands.
