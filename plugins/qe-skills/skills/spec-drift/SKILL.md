---
name: spec-drift
description: Detect drift between what is specified, what is built and what is tested. Compares requirements, API contracts, documentation, the implementation and the tests, and reports each mismatch (missing, extra, different behavior, outdated docs, tests that assert old behavior). Use when the user asks "does the code still match the spec?", before a release, after a refactor, or when the docs and the API seem out of date.
argument-hint: "[spec or contract path] [code area]"
---

# spec-drift

Over time, the spec, the code, the documentation and the tests tell different stories. Each difference is a bug, a missing feature, dead code or a stale document. This skill finds the differences and says which side is probably wrong.

## Input

The sources are in `$ARGUMENTS`: a spec, a contract (for example an API description), a documentation page, and the code area. If a source is missing, ask the user or search the repository for it.

## Steps

1. **Extract the claims.** From each source, list the concrete claims. Examples: endpoints or functions, fields and types, required and optional fields, allowed values, limits. Also error codes and messages, default values, status transitions, side effects and permissions.
   - spec and contract: what must be
   - documentation: what users are told
   - code: what is implemented (read the code paths, validation and mappings)
   - tests: what is checked (read the assertions, not the test names)
2. **Match the claims** across the sources by a key (endpoint and field, function and parameter, requirement ID).
3. **Classify each difference:**
   - MISSING IN CODE: specified, not implemented
   - EXTRA IN CODE: implemented, not specified (an undocumented behavior or a forgotten feature)
   - DIFFERENT: both exist, with a different value, type, limit, code or rule
   - STALE DOC: the documentation differs from the spec and the code
   - TEST ASSERTS OLD BEHAVIOR: a test checks a value that the spec no longer has
   - UNTESTED CLAIM: specified and implemented, but no test checks it
4. **Decide the likely truth** for each difference. The newest approved spec usually wins. If you cannot tell, write "ask the owner".
5. **Rank** by impact: a contract change that breaks clients is high.

## Output

```
## Spec drift: <scope>

Sources: spec <...>, contract <...>, docs <...>, code <...>, tests <...>
Claims compared: <n> | Differences: <d>

| # | Type | Key | Spec says | Code does | Docs say | Tests check | Likely truth | Impact |
|---|---|---|---|---|---|---|---|---|

### Actions
- Code to fix: ...
- Spec or docs to update: ...
- Tests to fix or add: ...
- Questions for the owner: ...
```

## Rules

- Quote each source with its location (file and line, or section).
- Do not change code, specs or tests in this skill. Report the drift.
- A difference is not always a code bug. Say which side to change, and why.
