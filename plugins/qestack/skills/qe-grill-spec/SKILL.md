---
name: qe-grill-spec
description: "Checks a spec before qestack test design: finds requirements without IDs, vague rules, missing examples and missing error behavior, and asks one question at a time. Use before qe-plan in a qestack repository, or when a spec has [NEEDS CLARIFICATION] items."
argument-hint: "[feature, for example 003-order-discount]"
---

# qe-grill-spec

Good tests need clear rules and concrete examples. This skill finds the gaps in the spec before anyone designs tests. It does not write tests.

## Steps

1. **Feature.** The feature is `$ARGUMENTS`. If it is empty, find the folder under `specs/` (speckit layout: `specs/<NNN-name>/spec.md`). If it is not clear, ask the user.
2. **IDs.** Run `qestack trace --feature <feature> --plan-only`. Use only the list of requirement IDs that it prints. Before a test plan exists, every ID shows "MISSING IN PLAN" and the exit code is 1. That is expected. Requirements without an ID are not traceable.
3. **Read** `spec.md`, and `contracts/` and `data-model.md` if they exist. For each requirement, check:
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
7. **Open gaps.** For each gap that is still open, propose a marker `[NEEDS CLARIFICATION: <question>]` at the requirement in `spec.md`. Add the markers after the user says "yes". The engine and `qe-plan` read these markers, and the test plan lists them as open questions.
8. **Report:** gaps found, gaps closed, open markers added. Next step: `qe-plan`.

## Rules

- Do not invent business rules. Ask.
- Do not read the implementation to "find" the rule. The spec is the source of truth.
