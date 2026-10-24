# Example: order discount (static gates)

This example shows what qestack finds in a typical AI-written test class. The test class looks complete: it has tests for each requirement, and most of them are green. qestack shows why it is still weak.

This example has no build file, so only the static gates run (`lint` and `trace`). A runnable Maven example comes in release 0.2.

## Run it

From the repository root:

```bash
QESTACK_ROOT=examples/order-discount qestack lint --feature 001
QESTACK_ROOT=examples/order-discount qestack trace --feature 001
```

## What you see

| Test | Finding | Why it matters |
|---|---|---|
| `hollowTest` | HOLLOW, TODO | It has no code. It always passes. |
| `noAssertionAtAll` | NO_ASSERTION, UNTRACED | It runs code but checks nothing, and has no requirement ID. |
| `statusOnly` | SHALLOW | It checks only the HTTP status. A wrong body passes. |
| `skipped` | SKIPPED, TRIVIAL | It does not run, and `assertEquals(1, 1)` checks nothing. |
| `nestedTest` | TRIVIAL, swallowed exception | `assertTrue(true)` and an empty `catch` hide every failure. |
| `customLib` | NO_ASSERTION, unknown ID `FR-099` | `ApiAssert` is a project helper that is not registered in `project.toml`, and the ID does not exist in the spec. Register your helpers with `/qe-setup`. |

`trace` also shows that FR-002 has no positive test and FR-003 has no negative test.

Then follow the [getting started guide](../../docs/getting-started.md) to see how `/qe-harden` fixes such tests.
