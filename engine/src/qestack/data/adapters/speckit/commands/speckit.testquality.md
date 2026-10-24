---
description: qestack - post-implementation quality gate. Hidden faults, mutation, flakiness, traceability, guard, an independent judge and an improvement loop until the quality bar is met or a human must decide. Run after /speckit.implement.
---

## User input

```text
$ARGUMENTS
```

## Steps

1. Find the feature as in `/speckit.testplan` step 1.
2. Use the `qe-harden` skill (`qestack:qe-harden` with the plugin) for this feature. The number of iterations comes from `[loop] max_iterations` in `.qestack/project.toml`.
3. The feature is complete only when the report says ACCEPT, or when a human signs off an ESCALATE report.
