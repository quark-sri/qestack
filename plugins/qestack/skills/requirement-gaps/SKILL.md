---
name: requirement-gaps
description: "Find gaps in requirements before tests or code exist: missing acceptance criteria and examples, vague words, undefined limits, units and rounding, missing error behavior and side effects, undefined states, roles and concurrency, conflicts between requirements. Gives focused questions with proposed answers. Use when: 'is this story testable', 'review these acceptance criteria', 'what is missing in this spec', 'refine this ticket'. Not for: designing test cases (use test-case-designer) or comparing the spec with the code (use spec-drift). Related: edge-case-hunter, test-case-designer, spec-drift."
argument-hint: "[spec, story, ticket or contract]"
---

# requirement-gaps

## Objective

Tests can only be as good as the rules behind them. A gap in a requirement becomes a bug or a wrong test later, and it costs more each phase. This skill finds what the requirement does not say, and turns each gap into a question with a proposed answer. It does not write tests or code.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its requirement ID format and the glossary.
2. If it does not exist, continue with the requirement source alone.

## Discovery questions

1. Where is the requirement: a file, a ticket, a contract, a design? Get all related sources.
2. Who answers the questions: a product owner, an analyst, a domain expert?

## Workflow

1. **Inventory.** List each requirement as one line, with its ID (give `R1`, `R2`, ... if there is none). Keep the original words.
2. **Check each requirement** against [the gap checklist](references/gap-checklist.md). Write one finding for each gap, with the exact quote.
3. **Check the set:**
   - contradictions between requirements
   - objects or states that no requirement defines
   - "create" with no rule for update, delete or read
   - roles that may and may not act
   - non-functional needs that the domain implies (audit, privacy, performance, accessibility)
4. **Rank:** high (money, security, data loss, legal, irreversible), medium (wrong result for some users), low (wording).
5. **Ask** the high gaps first. For each one, propose a concrete answer that the owner can accept or change.

## Output

```
## Requirement gaps: <source>

<n> requirements | high <h> | medium <m> | low <l>

| # | Req | Area | Quote | Gap | Risk | Question (proposed answer) |
|---|---|---|---|---|---|---|

Set-level gaps: ...
Ready for test design: <requirement IDs>
```

## Anti-patterns

- **Inventing rules.** A gap is a question, not an answer. The owner decides.
- **Reading the code to find the rule.** The code can be wrong.
- **Wording-only review.** Spelling and style are low value. Missing errors and limits are high value.

## Done when

- Each requirement was checked against the checklist.
- Each gap has a quote, a risk and a question with a proposed answer.
- The requirements that are ready for test design are listed.

## Related skills

- `edge-case-hunter`: the edge cases of the clarified requirement.
- `test-case-designer`: the test cases.
- `spec-drift`: compares the requirement with the code and the tests later.
