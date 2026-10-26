---
name: testability-review
description: "Scores how testable a feature, module or design is before tests exist (seams for clock, randomness and network, hidden state, observability) and gives the smallest production change per blocker. Use when the user asks 'is this testable' or 'why is this hard to test'. Not for writing the tests (use unit-testing)."
argument-hint: "[feature, module, design or pull request]"
---

# testability-review

## Objective

Hard-to-test code gets weak tests or no tests. Testability is cheapest to fix before the code exists. This skill finds what makes a behavior hard to control or to observe, scores it with evidence, and proposes the smallest change that fixes each blocker.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its stack, test levels and quality goals.
2. If it does not exist, find the test levels in the repository. Suggest `qa-project-context` once. Do not stop the work for it.

## Discovery questions

1. What is under review: a design, a plan, existing code or a change?
2. Which behavior must be tested, and at which level should the test run?
3. Which tests exist today, and what do they cost to write and to run?

## Principles

1. **Controllable and observable.** A behavior is testable when a test can set the inputs and can read the outputs and the effects.
2. **Seams, not rewrites.** Make a dependency replaceable with the smallest change, usually one parameter or one interface.
3. **Every score has evidence.** Quote the line or the design statement. Do not score from a feeling.
4. **Cost is the measure.** A rule that needs a real clock, a network or a long setup has a high test cost, and teams skip such tests.
5. **Propose, do not change.** Production changes belong to the owner of the code.

## Workflow

1. Name the behaviors in scope. For a design with no code, use the requirements and the interfaces.
2. Check each behavior with [the testability checklist](references/testability-checklist.md). Record a score from 0 (blocked) to 2 (easy) for each factor, with the evidence.
3. Give the total for each behavior and mark the blockers: factors with a score of 0.
4. For each blocker, write the smallest production change (seam, parameter, interface, log or flag) and the test it makes possible.
5. Rank the changes by the risk of the behavior and the cost of the change.
6. Report the scores, the blockers, the changes and the tests that stay impossible at this level.

## Anti-patterns

- **Calling code "untestable".** Name the factor and the seam.
- **A rewrite as the fix.** Look for the smallest seam first.
- **Test-only hooks in production,** such as a flag that changes the behavior when a test runs. Use a real seam.
- **Scoring only style.** Long methods are a smell. They matter only when they block control or observation.

## Done when

- Each behavior in scope has a score for each factor, with evidence.
- Each blocker has a concrete change and the test it enables.
- The changes are ranked, and the owner knows which ones to do first.

## Related skills

- `unit-testing`: writes the tests after the seams exist.
- `requirement-gaps`: finds missing rules that also make testing hard.
- `roast-my-code`: a wider review of the code.
- `test-strategy`: sets the testability goals for a team.
