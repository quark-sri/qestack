---
name: bug-report
description: Write a clear, reproducible defect report from a failing test, a log, a user complaint or a finding. Includes a precise title, environment, minimal reproduction steps, expected result with its source, actual result, evidence, severity and priority, impact and a regression test idea. Use when the user asks to write, file or improve a bug report, or after a bug is found by a test or review.
argument-hint: "[failing test, log, issue text or finding]"
---

# bug-report

A good bug report lets another person see the bug in minutes, without a meeting. This skill writes such a report, and it checks the facts first.

## Input

The source is `$ARGUMENTS`: a failing test, an error log, a stack trace, a user message, or a finding from a review. If it is empty, ask the user.

## Steps

1. **Confirm the bug.** Find the requirement or the documented behavior that the actual result breaks. If none exists, it can be a missing requirement. Write that as a question, not as a bug.
2. **Reproduce.** Find the shortest steps or the smallest test that shows the problem. Remove each step that is not needed. Record the exact data and the environment (version or commit, configuration, browser or client, platform, time zone if it matters).
3. **Narrow down.** Note what does NOT show the bug (other data, other users, an earlier version). This helps the developer find the cause. If the version history is available, name the first version or commit that shows the bug.
4. **Collect evidence:** the error message, the relevant log lines, the stack trace, a request and a response, the failing test name. Remove secrets and personal data.
5. **Rate:**
   - severity (effect on the system): critical (data loss, security, crash of a main path, money), major (wrong result, no workaround), minor (workaround exists), trivial (cosmetic)
   - priority (urgency for the business): ask the user, or propose one with a reason
6. **Write the report** in the format below. Check that a reader who knows the product but not the code can follow it.

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
Evidence: <test name, log lines, request/response, screenshot reference>
Impact: <who is affected, how often, what it costs>
Regression test: <the test that must exist after the fix>
```

## Rules

- One bug in each report. Split a report that describes two problems.
- Facts only: no guess about the cause in the steps. Put a cause hypothesis in a separate, labeled line.
- Do not file the report in a tracker without the user's approval.
