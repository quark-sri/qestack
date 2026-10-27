---
name: edge-case-hunter
description: "Finds edge, boundary and negative cases for a feature, function, endpoint or form from a catalog (numbers, text, time, money, state, concurrency, security), each with an input and an expected result. Use when the user asks 'what edge cases am I missing'. Not for a full test design (use test-case-designer)."
license: MIT
argument-hint: "[feature, function, endpoint or file]"
---

# edge-case-hunter

## Objective

Most escaped defects live at the edges: the limit value, the empty input, the second request, the end of the month. This skill lists the edge cases that matter for one target, with a concrete input and the expected result for each one, and shows which ones the tests already cover.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its risk areas and conventions.
2. If it does not exist, continue with the target alone.

## Discovery questions

1. What is the target, and where is its requirement or contract?
2. Do tests exist for it? Where?

## Workflow

1. **Model the target.** List:
   - each input (parameters, fields, headers, files, messages, configuration, time, the current user)
   - each output and side effect (return value, response, stored data, messages, calls to other systems)
   - each state that changes the behavior (status, feature flag, role, tenant, existing data)
   - each dependency that can fail
2. **Hunt.** For each input, state and dependency, use the matching sections of [the edge case catalog](references/edge-case-catalog.md). Keep only the cases that apply.
3. **Combine** the cases that matter together: two inputs at their limits, a valid input in a wrong state, a retry after a partial failure.
4. **Expected result** from the requirement. If the requirement does not say, write "UNDEFINED" and a question. Do not guess.
5. **Existing tests.** Mark each case as covered, partly covered or missing.
6. **Rank** by risk: the likelihood that the code is wrong times the impact.

## Output

```
## Edge cases: <target>

| # | Area | Case | Input / setup | Expected (source) | Risk | Covered? |
|---|---|---|---|---|---|---|

Undefined behavior (questions): ...
Top 5 to add first: ...
```

## Anti-patterns

- **"Test invalid input".** Each case needs a real value or setup.
- **The expected result from the code.** It confirms the current behavior, also when it is wrong.
- **Cases that every implementation passes.** They add run time and no protection.

## Done when

- Each input, state and dependency was checked against the catalog.
- Each kept case has a concrete input, an expected result with a source or "UNDEFINED", a risk and a coverage status.
- The top cases to add are listed.

## Related skills

- `test-case-designer`: turns the cases into test cases.
- `requirement-gaps`: for the undefined behavior.
- `exploratory-testing`: tries the cases by hand.
- `bug-hunter`: checks the code for the risky cases.
