---
name: accessibility-testing
description: "Tests web and app accessibility against WCAG level AA: automated rule checks, keyboard and focus order, names and roles, contrast, forms and manual screen reader checks. Use when the user says 'accessibility test', 'a11y', 'WCAG' or 'screen reader'. Not for general UI journeys (use ui-automation)."
license: Apache-2.0
argument-hint: "[page, component or user journey]"
---

# accessibility-testing

## Objective

An inaccessible product shuts out users and can break the law. Automated checks find only part of the problems; keyboard and screen reader checks find the rest. This skill combines both, starting with the critical journeys.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its critical journeys, UI test framework and quality goals.
2. If it does not exist, find the UI test framework in the repository. Suggest `qa-project-context` once.

## Discovery questions

1. Which standard and level is the target (for example WCAG 2.2 AA), and is there a legal requirement?
2. Which journeys are critical?
3. Which UI test framework is used, so that rule checks can run in the existing tests?

## Principles

1. **Automated rule checks catch only part of the problems.** They are a floor, not a proof.
2. **Keyboard first.** Every action works with the keyboard alone, with a visible focus in a logical order.
3. **Names, roles and states** come from the semantics of the markup. They also make UI tests stable.
4. **Test the dynamic states:** errors, dialogs, menus, loading, toasts, not only the first page view.
5. **Real assistive technology for critical journeys:** a screen reader check by a person.

## Workflow

1. List the journeys and the components in scope, and their dynamic states.
2. Add automated rule checks to the UI tests for each page and each important state (see the stack recipe). Fail on serious and critical violations; track the rest.
3. Do a keyboard pass for each journey with [the manual checklist](references/manual-checklist.md).
4. Check zoom to 200% and a narrow screen for reflow, and the color contrast of text and controls.
5. Do a screen reader pass for the critical journeys.
6. Report each issue with the guideline, the element, the user impact and a fix.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own tools, and say so.

## Anti-patterns

- **"The scanner is green, so it is accessible."**
- **Only the first page state is checked.** Errors and dialogs are not.
- **Disabling rules** to make the check pass, without a ticket.

## Done when

- Automated rule checks run in the UI tests for each page and state in scope, and block on serious violations.
- Each critical journey passed a keyboard check and a screen reader check, or the gaps are listed.
- Each issue has the guideline, the impact and a fix.

## Related skills

- `ui-automation`: the tests that run the rule checks.
- `exploratory-testing`: keyboard and screen reader sessions.
- `ci-cd-integration`: the checks in the pipeline.
