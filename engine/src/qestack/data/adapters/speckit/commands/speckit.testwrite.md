---
description: qestack - write the feature tests "blind" from test-plan.md, prove that they fail before the implementation, and lock them. Run after /speckit.tasks and before /speckit.implement.
---

## User input

```text
$ARGUMENTS
```

## Steps

1. Find the feature as in `/speckit.testplan` step 1.
2. Use the `qe-write` skill (`qestack:qe-write` with the plugin) for this feature.
3. If `qe-write` reports no lint or trace failure and no guard violation, use the `qe-prove` skill (`qestack:qe-prove`) for this feature. Otherwise stop and show the failures.
4. Tell the user: test tasks in `tasks.md` refer to the `TC-###` IDs in `test-plan.md`. `/speckit.implement` must not create these tests again and must not weaken them. Next step: `/speckit.implement`, then `/speckit.testquality`.
