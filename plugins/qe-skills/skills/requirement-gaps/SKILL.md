---
name: requirement-gaps
description: Find gaps in requirements before anyone designs or writes tests. Checks a user story, spec, ticket, PRD or API contract for missing acceptance criteria, vague words, undefined limits, missing error behavior, unstated assumptions and conflicts, then asks focused questions. Use when the user asks "is this story testable?", "what is missing in this spec?", or gives requirements before test design.
argument-hint: "[path to the spec, story or ticket text]"
---

# requirement-gaps

Tests can only be as good as the rules behind them. This skill finds what the requirement does not say, before the gap becomes a bug or a wrong test. It does not write tests or code.

## Input

The requirement source is `$ARGUMENTS`: a file, a folder, a ticket text, or a description from the user. If it is empty, ask the user for it. Also read the related contracts, data models, designs and glossaries if they exist.

## Steps

1. **Inventory.** List each requirement as one line. Give each one an ID if it has none (`R1`, `R2`, ...). Keep the original wording.
2. **Check each requirement** against the checklist below. Write one finding for each gap. Quote the exact text.
3. **Check the requirement set as a whole:**
   - two requirements that contradict each other
   - a business object or state that one requirement uses and no requirement defines
   - a rule for "create" with no rule for "update", "delete" or "read"
   - roles and permissions: who may do it, and who may not
   - non-functional needs that the domain implies (audit, privacy, performance, accessibility) but that the text does not state
4. **Rank** the gaps: high (money, security, data loss, legal, irreversible actions), medium (wrong result for some users), low (wording).
5. **Ask.** Give the user the high gaps first, as questions. For each question, propose a concrete answer that the user can accept or change. Ask about one area at a time.
6. **Report** in the format below.

## Checklist for each requirement

| Area | Gap to find |
|---|---|
| Example | No concrete example with input and expected output |
| Limits | A number, length, size, date or count with no limit, or a limit that does not say if it is included ("over 100": is 100 in?) |
| Units and precision | Money without currency or rounding rule; time without time zone; size without unit |
| Errors | Invalid input with no defined result (message, code, status, state after the error) |
| Effects | It does not say what is saved, sent or changed, and what must NOT change on failure |
| States | A status field with no list of allowed transitions |
| Actors | No actor, or "the system" does something with no trigger |
| Vague words | "fast", "easy", "user-friendly", "appropriate", "some", "etc.", "and/or", "should" (is it a must?) |
| Defaults | An optional input with no default value |
| Concurrency | Two users or two requests at the same time, with no rule |
| Time | Expiry, scheduling, daylight saving, end of month, leap year, with no rule |
| Data | Empty, null, duplicate, very large, special characters, other languages, with no rule |
| Testability | A statement that no test can check ("the code is clean", "works well") |

## Output

```
## Requirement gaps: <source>

Summary: <n> requirements, <h> high / <m> medium / <l> low gaps

| # | Req | Area | Quote | Gap | Risk | Question (proposed answer) |
|---|---|---|---|---|---|---|

### Set-level gaps
- ...

### Ready for test design
<the requirements with no high or medium gap>
```

## Rules

- Do not invent business rules. A gap is a question, not an answer.
- Do not read the implementation to find the rule. The code can be wrong.
- Quote the requirement text for each finding, so that the author can find it.
- Next steps for the user: `edge-case-hunter`, then `test-case-designer`.
