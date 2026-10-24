---
name: test-review-panel
description: "Review tests or a change with a panel of independent reviewer personas, then merge their findings into one ranked list with no duplicates. The panel: AI Behavior Auditor, Hallucination Checker, Domain Oracle Reviewer, Saboteur, Test Automation Architect, Determinism and Flakiness Engineer, Maintainability Craftsperson, and Suite Cost and Speed Reviewer. Use when: 'review panel', 'full review of these tests', 'review AI-written tests from all angles', 'is this change safe to merge', 'deep test review'. Not for: a quick score of a few tests (use testcase-reviewer) or one question only, such as faults (use mutation-probe) or flakiness (use flaky-test-detective). Related: testcase-reviewer, mutation-probe, flaky-test-detective, test-strategy, release-readiness."
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
4. Can the panel run tests? The Saboteur and the Determinism and Flakiness Engineer need a clean working tree and a safe test command.

## The panel

| Persona | Persona file | Asks | Default |
|---|---|---|---|
| AI Behavior Auditor | [`ai-behavior-auditor`](references/personas/ai-behavior-auditor.md) | Did the author take a shortcut to make it green? | AI-written work |
| Hallucination Checker | [`hallucination-checker`](references/personas/hallucination-checker.md) | Does each name, flag, path and version exist? | AI-written work |
| Domain Oracle Reviewer | [`domain-oracle-reviewer`](references/personas/domain-oracle-reviewer.md) | Do the tests expect the right results? | always |
| Saboteur | [`saboteur`](references/personas/saboteur.md) | Do the tests fail when the code is wrong? | when tests can run |
| Test Automation Architect | [`test-automation-architect`](references/personas/test-automation-architect.md) | Is each test at the right level, in a design that lasts? | suite or large change |
| Determinism and Flakiness Engineer | [`determinism-flakiness-engineer`](references/personas/determinism-flakiness-engineer.md) | Does the test give the same result every time? | always |
| Maintainability Craftsperson | [`maintainability-craftsperson`](references/personas/maintainability-craftsperson.md) | Can the next person read, change and diagnose it? | always |
| Suite Cost and Speed Reviewer | [`suite-cost-speed-reviewer`](references/personas/suite-cost-speed-reviewer.md) | Where do the time and the money go? | suite or pipeline |

Each persona file has a mode (read-only or changes code), a scope, a checklist, an evidence rule, an output table and limits. The persona files are part of this skill, so they travel with it. This skill is the only one that uses them. The other skills in this plugin work without them.

**Two reviewers, many personas.** The `mode` of the persona file chooses the agent of this plugin:

- `read-only`: the `test-reviewer` agent. It has no edit tool.
- `changes-code`: the `test-saboteur` agent. It can change production code, and it restores it.

The lead starts one agent for each persona, with the persona file in the brief. If the host has no such agents, start any separate reviewer and give it the persona file. If the host cannot start separate reviewers, use the reduced mode in step 3.

## Principles

1. **Independence.** Each persona works in its own context, with no view of the other findings. The author of the work is never on the panel.
2. **Read-only.** Only the Saboteur changes code, one fault at a time, and it restores the code. No persona fixes anything.
3. **Evidence or nothing.** A finding without file and line goes to "questions", not to the ranked list.
4. **The lead checks.** The lead reads the evidence for each blocker and each major finding before it accepts it.

## Workflow

1. **Scope.** List the files, the requirement sources, the test command and the facts from the context file. This is the brief.
2. **Choose the panel.** Use the "Default" column, or the `--personas` list from the user. Say which personas you chose and why.
3. **Start one agent for each persona.** Each brief has the same scope and facts, and the path of one persona file. Start the `read-only` personas in parallel with `test-reviewer`. Then start each `changes-code` persona alone with `test-saboteur`, because it changes files and runs tests. If the host cannot start separate reviewers, read each persona file and apply it yourself, one at a time. Say in the report that the review was not independent.
4. **Verify.** For each blocker and major finding, open the evidence. Reject findings that the evidence does not support, and say why.
5. **Merge.** Two findings are the same when they have the same root cause at the same place. Keep the strongest evidence, list all personas that found it, and use the highest severity.
6. **Rank.** Blockers first, then by how a defect could reach users: wrong results, missing protection, false confidence, then cost and readability.
7. **Check the tree.** Confirm that the working tree is equal to the start.

## Output

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
- **The Saboteur in parallel with test runs.** Its faults change the results of the other personas.

## Done when

- Each chosen persona reported, or the report says which one did not and why.
- Each blocker and major finding has evidence that the lead checked.
- The findings are merged, ranked and have a fix.
- The working tree is equal to the start.

## Related skills

- `testcase-reviewer`: a quick rubric score, with no panel.
- `mutation-probe`: the Saboteur method in depth.
- `flaky-test-detective`: the root cause of one flaky test.
- `test-strategy`: the long-term direction, when the Architect finds design problems.
- `release-readiness`: uses the panel verdict as evidence.
