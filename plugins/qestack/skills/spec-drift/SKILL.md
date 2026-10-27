---
name: spec-drift
description: "Detects drift between what is specified, documented, built and tested, and reports each mismatch with the likely truth and the side to change. Use when the user asks 'does the code still match the spec' or 'are the docs up to date'. Not for gaps inside the requirements (use requirement-gaps)."
license: MIT
argument-hint: "[spec or contract] [code area]"
---

# spec-drift

## Objective

Over time, the spec, the code, the documentation and the tests tell different stories. Each difference is a bug, a missing feature, dead code or a stale document. This skill finds the differences and says which side is probably wrong.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its requirement sources and contract files.
2. If it does not exist, search the repository for the specs, contracts and documentation. Do not stop the work for the context file.

## Discovery questions

1. Which sources are in scope: a spec, a contract, a documentation page, a code area, the tests?
2. Which source is the approved truth when two sources differ?

## Workflow

1. **Extract the claims** from each source. Examples: endpoints or functions, fields and types, required and optional fields, allowed values, limits. Also error codes and messages, defaults, status transitions, side effects and permissions.
   - spec and contract: what must be
   - documentation: what users are told
   - code: what is implemented (code paths, validation, mappings)
   - tests: what is checked (the assertions, not the test names)
2. **Match the claims** by a key (endpoint and field, function and parameter, requirement ID).
3. **Classify each difference:** MISSING IN CODE, EXTRA IN CODE, DIFFERENT, STALE DOC, TEST ASSERTS OLD BEHAVIOR, UNTESTED CLAIM.
4. **Decide the likely truth.** The newest approved spec usually wins. If you cannot tell, write "ask the owner".
5. **Rank** by impact. A contract change that breaks clients is high.

## Output

```
## Spec drift: <scope>

Claims compared: <n> | Differences: <d>

| # | Type | Key | Spec says | Code does | Docs say | Tests check | Likely truth | Impact |
|---|---|---|---|---|---|---|---|---|

Actions: code to fix / spec or docs to update / tests to fix or add / questions for the owner
```

## Anti-patterns

- **Assuming the code is right** because it runs in production.
- **Reading test names instead of assertions.** A test named "rejects negative totals" may check nothing.
- **Changing sources in this skill.** Report the drift; the owners decide.

## Done when

- Each claim in scope is matched across the sources, with a location for each quote.
- Each difference has a type, a likely truth and an impact.
- The actions are listed for code, docs, spec and tests.

## Related skills

- `requirement-gaps`: gaps inside the spec.
- `contract-testing`: stops contract drift between services.
- `test-coverage-map`: the untested claims in depth.
- `api-testing`: tests for the drifted endpoints.
