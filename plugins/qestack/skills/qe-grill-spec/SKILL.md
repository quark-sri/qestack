---
name: qe-grill-spec
description: Check that a specification is testable before test design. Finds requirements without IDs, vague rules, missing examples, missing error behavior and untestable statements, and asks the user one question at a time. Use before qe-plan, or when a spec has [NEEDS CLARIFICATION] items.
---

# qe-grill-spec

Good tests need clear rules and concrete examples. This skill finds the gaps in the spec before anyone designs tests. It does not write tests.

## Steps

1. Find the feature folder (speckit layout: `specs/<NNN-name>/spec.md`). If it is not clear, ask the user.
2. Run `qestack trace --feature <feature> --plan-only` to see the requirement IDs that the engine finds. Requirements without an ID are not traceable.
3. Read `spec.md`, `contracts/` and `data-model.md`. For each requirement, check:
   - **ID:** It has an ID (`FR-###`, or a numbered acceptance scenario under a "User Story" heading).
   - **Example:** It has at least one concrete example with input and expected output.
   - **Limits:** Each number, size or date limit says if the limit itself is included.
   - **Errors:** Invalid input has a defined result (status, error code, message key).
   - **Effects:** It says what is saved, what events are sent, and what does NOT change on failure.
   - **Measurable:** It has no vague words ("fast", "user-friendly", "appropriate", "etc.").
   - **Conflicts:** It does not contradict another requirement or a contract.
4. Make a numbered list of gaps, highest risk first (money, security, data integrity).
5. Ask the user about the gaps, **one question at a time**. For each question, suggest a concrete answer that the user can accept or change.
6. Collect the answers. Show the proposed spec changes as a diff. Write them to `spec.md` only after the user says "yes". (With speckit, the user can also run `/speckit.clarify`.)
7. List the gaps that are still open. They become open questions in the test plan.

## Rules

- Do not invent business rules. Ask.
- Do not read the implementation to "find" the rule. The spec is the source of truth.
