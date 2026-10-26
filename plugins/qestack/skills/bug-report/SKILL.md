---
name: bug-report
description: "Write a clear, reproducible defect report from a failing test, a log, a stack trace, a user complaint or a review finding: confirm the expected behavior, find minimal reproduction steps or a failing test, narrow down where it does and does not happen, collect evidence without secrets, rate severity and priority, and add the impact and a regression test idea. Use when: 'write a bug report', 'file this bug', 'improve this ticket', 'turn this failure into a bug report', 'minimal repro'. Not for: hunting new bugs in code (use bug-hunter) or classifying many pipeline failures (use test-runner). Related: bug-hunter, test-runner, quality-postmortem, exploratory-testing."
argument-hint: "[failing test, log, issue text or finding]"
---

# bug-report

## Objective

A good bug report lets another person see the bug in minutes, without a meeting. This skill writes such a report, and it checks the facts first.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its environments, components and severity rules.
2. If it does not exist, collect the facts from the source and the repository. Do not stop the work for the context file.

## Discovery questions

1. What is the source of the bug, and where does it happen?
2. Which tracker and template does the team use? Who sets the priority?

## Workflow

1. **Confirm the bug.** Find the requirement or documented behavior that the actual result breaks. If none exists, it can be a missing requirement: write it as a question.
2. **Reproduce** with the shortest steps or the smallest failing test. Remove each step that is not needed. Record the exact data and the environment (version or commit, configuration, client, platform, time zone if it matters).
3. **Narrow down:** what does NOT show the bug (other data, users, versions). If the history is available, name the first version or commit that shows it.
4. **Evidence:** the error message, relevant log lines, the stack trace, a request and a response, the failing test name. Remove secrets and personal data.
5. **Rate** severity (critical: data loss, security, crash of a main path, money; major: wrong result, no workaround; minor: workaround exists; trivial: cosmetic). Propose a priority with a reason, or ask.
6. **Write** the report, and check that a reader who knows the product but not the code can follow it.

## Output

```
Title: <component>: <what is wrong> when <condition>

Environment: <version/commit, configuration, platform>
Severity: <..>   Priority (proposed): <..>

Steps to reproduce:
1. ...

Expected result: ... (source: <requirement, contract or document>)
Actual result: ...
Frequency: always | sometimes (<n> of <m> runs)
Does not happen when: ...
Evidence: ...
Impact: <who, how often, what it costs>
Regression test: <the test that must exist after the fix>
Cause hypothesis (optional, labeled): ...
```

## Anti-patterns

- **Two bugs in one report.**
- **A guess about the cause in the steps.** Keep it in the labeled hypothesis line.
- **Secrets or personal data** in the evidence.
- **Filing in the tracker** without the user's approval.

## Done when

- The expected result has a source, and the steps reproduce the bug (or the frequency is stated).
- The evidence is clean of secrets and personal data.
- Severity, proposed priority, impact and a regression test are stated.

## Related skills

- `bug-hunter`: finds and proves bugs in code.
- `test-runner`: triages failures.
- `quality-postmortem`: when the bug escaped to production.
- `exploratory-testing`: bugs found in sessions.
