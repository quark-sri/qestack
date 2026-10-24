---
description: qestack - post-implementation quality gate. Hidden faults, mutation, flakiness, traceability, guard, an independent judge and an improvement loop until the quality bar is met or a human must decide. Run after /speckit.implement.
---

## User input

```text
$ARGUMENTS
```

## Steps

1. Find the feature as in `/speckit.testplan` step 1.
2. Use the **qe-harden** skill for this feature. Pass the user input (for example a maximum number of iterations).
3. The feature is complete only when the report says ACCEPT, or when a human signs off an ESCALATE report.
