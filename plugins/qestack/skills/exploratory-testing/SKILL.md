---
name: exploratory-testing
description: "Plan, run and report session-based exploratory testing: charters from risks and heuristics, time-boxed sessions, notes on what was tested, bugs, questions and new test ideas, and a debrief. Use when: 'exploratory testing', 'explore this feature', 'manual testing session', 'test charter', 'find bugs by hand before release'. Not for: scripted regression cases (use test-case-designer) or bug hunting in source code (use bug-hunter). Related: risk-based-testing, edge-case-hunter, bug-report, test-case-designer."
argument-hint: "[feature, area or release]"
---

# exploratory-testing

## Objective

Scripted tests check what the team already knows. Exploratory testing finds what nobody thought of. Session-based exploration keeps it focused and accountable: each session has a mission, a time box and a written result.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its critical journeys, risk areas and environments.
2. If it does not exist, ask the user for the environment, the accounts and the area. Suggest `qa-project-context` once.

## Discovery questions

1. Which area, and which environment? Which accounts, roles and test data are available?
2. What changed recently, and what are the known risks?
3. How much time is there, and how many sessions?

## Workflow

1. **Charters.** Write 3 to 8 charters in the form "Explore <target> with <resources or technique> to discover <information or risk>". Take them from the top risks, the recent changes and [the exploration heuristics](references/heuristics.md).
2. **Session (45 to 90 minutes each).** For each charter:
   - Follow the mission, and note the new risks for later charters.
   - Record what you tested, the data you used, and what you observed.
   - When something looks wrong, record the exact steps, the data and the evidence at once.
3. **Session sheet** for each session: charter, time, areas covered, bugs, questions, blocking issues and new test ideas. Also note the share of time for testing, for setup and for bug investigation.
4. **Debrief.** Summarize the risks found, the areas not covered, and the follow-ups. Turn each confirmed bug into a report (see `bug-report`). Turn each repeatable check into an automation candidate.

## Anti-patterns

- **Random clicking.** A session with no charter gives no coverage information.
- **No notes.** A bug without exact steps and data cannot be reproduced.
- **Only the happy path.** Use the heuristics: limits, interruptions, wrong order, other roles.

## Done when

- Each charter has a session sheet.
- Each bug has steps, data and evidence.
- The debrief lists the risks, the uncovered areas, the follow-ups and the automation candidates.

## Related skills

- `risk-based-testing`: the risks for the charters.
- `edge-case-hunter`: the edge cases to try.
- `bug-report`: the reports for the bugs found.
- `test-case-designer`: the scripted cases for the repeatable checks.
