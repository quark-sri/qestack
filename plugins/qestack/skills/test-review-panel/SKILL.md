---
name: test-review-panel
description: "Reviews tests or a change with up to 8 independent read-only reviewer personas, then merges their findings into one ranked list. Use when the user says 'review panel' or 'deep test review', asks 'is this change safe to merge', or wants AI-written tests reviewed from all angles. Not for a quick score (use testcase-reviewer)."
license: Apache-2.0
argument-hint: "[tests, change or pull request] [--personas a,b,c]"
---

# test-review-panel

## Objective

One reviewer sees one kind of problem. A panel of reviewers with different jobs sees more, if each one stays in its lane and gives evidence. This skill starts the right personas, each as an independent read-only reviewer, and then acts as the lead: it checks, merges, deduplicates and ranks their findings.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Give each persona the parts it needs: the stack, the test commands, the requirement sources and the conventions.
2. If it does not exist, collect the test command and the requirement sources yourself. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. What is in scope: some test files, a change, a pull request or a whole suite?
2. Where are the requirements or the documented behavior?
3. Did an AI agent write the work? Then the AI Behavior Auditor and the Hallucination Checker are required.
4. Can the panel run tests? The fault plan of the Saboteur needs a safe test command and an isolated copy of the repository. The Determinism and Flakiness Engineer needs a safe test command.
5. Where do the reports go? Use the `Review reports` line of the context file, or `qa-reviews/`. On the first run, ask once whether the team commits this folder or ignores it in version control.

## The panel

| Persona | Agent | Asks | Default |
|---|---|---|---|
| AI Behavior Auditor | `ai-behavior-auditor` | Did the author take a shortcut to make it green? | AI-written work |
| Hallucination Checker | `hallucination-checker` | Does each name, flag, path and version exist? | AI-written work |
| Domain Oracle Reviewer | `domain-oracle-reviewer` | Do the tests expect the right results? | always |
| Saboteur | `saboteur` | Do the tests fail when the code is wrong? | when tests can run |
| Test Automation Architect | `test-automation-architect` | Is each test at the right level, in a design that lasts? | suite or large change |
| Determinism and Flakiness Engineer | `determinism-flakiness-engineer` | Does the test give the same result every time? | always |
| Maintainability Craftsperson | `maintainability-craftsperson` | Can the next person read, change and diagnose it? | always |
| Suite Cost and Speed Reviewer | `suite-cost-speed-reviewer` | Where do the time and the money go? | suite or pipeline |

Each persona is an agent of this plugin, with only the tools that its job needs. No persona has an edit tool. Personas find and report. The lead, this skill, makes any change. Each persona has a scope, a checklist, an evidence rule, an output table, limits and the same "Reviewer rules". The rules make each persona return its report and a findings block, and write no files. This skill is the only skill in this plugin that uses the personas. The other skills work without them. Users can also start a persona directly, or from their own skills.

## Principles

1. **Independence.** Each persona works in its own context, with no view of the other findings. The author of the work is never on the panel.
2. **Personas report, the lead acts.** No persona changes a file. The Saboteur only designs faults. The lead runs its fault plan in an isolated copy. No one fixes anything during the review.
3. **Evidence or nothing.** A finding without file and line goes to "questions", not to the ranked list.
4. **The lead checks.** The lead reads the evidence for each blocker and each major finding before it accepts it.

## Workflow

1. **Scope.** List the files, the requirement sources, the test command and the facts from the context file. Say if the personas may run tests against a shared environment; the default is no. This is the brief.
2. **Choose the panel.** Use the "Default" column, or the `--personas` list from the user. Say which personas you chose and why.
3. **Start the persona agents in parallel.** Each one gets the same brief. If the host cannot start these agents, give the text of each agent file to a separate reviewer. If the host cannot start separate reviewers, apply each agent file yourself, one at a time. Say in the report that the review was not independent.
4. **Run the fault plan.** If the Saboteur returned a fault plan, run it with the method of `mutation-probe`: in an isolated copy, one fault at a time. Mark each predicted survivor as proven or wrong. Do this after all personas have reported, so that no persona sees a fault.
5. **Verify.** For each blocker and major finding, open the evidence. Reject findings that the evidence does not support, and say why.
6. **Merge.** Two findings are the same when they have the same root cause at the same place. Keep the strongest evidence, list all personas that found it, and use the highest severity.
7. **Rank.** Blockers first, then by how a defect could reach users: wrong results, missing protection, false confidence, then cost and readability.
8. **Check the tree.** Confirm that the working tree is equal to the start. Do this before you write the reports, so that the check sees only the code.
9. **Save.** Check each findings block with [the findings format](references/findings-format.md). Then write the review folder: `panel-report.md`, `findings.json` and `personas/<name>.md`, as [the findings format](references/findings-format.md) says. Never overwrite an earlier run.
10. **Hand over.** Show the verdict, the top findings and the folder path in the conversation. Offer to publish `panel-report.md` as a shareable page, or to post it as a pull request comment, if the host can do this. Do not publish without a yes.

## Output

The review folder (default `qa-reviews/<YYYY-MM-DD>-<scope-slug>/`):

```
panel-report.md        merged, ranked findings and the verdict, for people
findings.json          the same findings, machine-readable, for pipelines and trends
personas/<name>.md     the full message of each reviewer, unchanged
```

`panel-report.md`:

```
## Test review panel: <scope>

Panel: <personas> | Independent: yes or no | Working tree restored: yes
Findings: <n> | blocker <b> | major <m> | minor <x> | rejected by the lead <r>

| # | Severity | Finding | Evidence (file:line) | Found by | Fix |
|---|---|---|---|---|---|
| 1 | blocker | discount boundary expected wrong, and the fault survives | DiscountTest:31, Discount.java:27 | domain-oracle-reviewer, saboteur | expect 90.00 at exactly 100.00 |

Verdict: ready | ready after fixes 1-3 | not ready
Rejected findings (with reason): ...
Questions for a person: ...
```

## Anti-patterns

- **A panel of one.** One context that "plays" all personas at once sees the same things eight times.
- **Pasting eight reports.** The lead must merge and rank. The user wants one list.
- **Counting votes.** Three personas that agree on a weak finding do not make it strong. Evidence does.
- **Faults while personas run.** A fault in the code changes what the other personas see. Run the fault plan after all reports, in an isolated copy.
- **Reviewers that write files.** Reviewers return their reports. Only the lead changes files: it runs the fault plan and writes the review folder, after the tree check.

## Done when

- Each chosen persona reported, or the report says which one did not and why.
- Each blocker and major finding has evidence that the lead checked.
- The findings are merged, ranked and have a fix.
- The working tree is equal to the start.
- The review folder has `panel-report.md`, `findings.json` and one file for each persona, and the user has its path.

## Related skills

- `testcase-reviewer`: a quick rubric score, with no panel.
- `mutation-probe`: runs the fault plan of the Saboteur in an isolated copy.
- `flaky-test-detective`: the root cause of one flaky test.
- `test-strategy`: the long-term direction, when the Architect finds design problems.
- `release-readiness`: uses the panel verdict as evidence.
