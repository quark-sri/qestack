---
name: edge-case-hunter
description: Hunt the edge, boundary and negative cases for a feature, function, API endpoint, form or data flow. Uses a catalog of edge cases by data type and by domain (numbers, strings, dates, money, collections, files, concurrency, state, security, integrations). Use when the user asks "what edge cases am I missing?", "what could break this?", or wants negative and boundary cases before or after writing tests.
argument-hint: "[feature, function, endpoint or file]"
---

# edge-case-hunter

Most escaped defects live at the edges: the limit value, the empty input, the second request, the end of the month. This skill lists the edge cases that matter for one target, with a concrete input and the expected result for each one.

## Input

The target is `$ARGUMENTS`: a requirement, a function, an endpoint, a screen or a message flow. If it is empty, ask the user. Read the requirement or contract first. Read the code only to find the inputs, the outputs and the dependencies, not to decide the expected result.

## Steps

1. **Model the target.** List:
   - each input (parameters, fields, headers, files, messages, configuration, time, the current user)
   - each output and side effect (return value, response, stored data, events, calls to other systems, logs)
   - each state that changes the behavior (status, feature flag, role, tenant, cache, existing data)
   - each dependency that can fail (database, other services, queue, file system, clock, network)
2. **Hunt.** For each input, state and dependency, go through the matching sections of [the edge case catalog](references/edge-case-catalog.md). Keep only the cases that apply to this target.
3. **Combine.** Add the combinations that matter: two inputs at their limits together, a valid input in a wrong state, a retry after a partial failure.
4. **Expected result.** For each case, write the expected result from the requirement. If the requirement does not say, write "UNDEFINED" and a question for the requirement owner. Do not guess.
5. **Check existing tests** if they exist. Mark each case as covered, partly covered or missing. Search the test code for the input value or the behavior.
6. **Rank** by risk: likelihood that the code is wrong times the impact of the failure.

## Output

```
## Edge cases: <target>

| # | Area | Case | Input / setup | Expected result (source) | Risk | Covered? |
|---|---|---|---|---|---|---|

### Undefined behavior (questions)
- ...

### Top 5 to add first
1. ...
```

## Rules

- Each case is concrete: a real value or a real setup, not "test invalid input".
- The expected result comes from the requirement, a contract or a documented rule. Never from what the code does now.
- Prefer cases that a wrong implementation would fail. Skip cases that every implementation passes.
- Next step for the user: `test-case-designer` to turn the cases into test cases.
