---
description: qestack - design a spec-first test plan (test-plan.md) for the current feature and get an independent plan review. Run after /speckit.plan and before /speckit.tasks.
---

## User input

```text
$ARGUMENTS
```

## Steps

1. Find the feature. From the repository root run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` (Windows: `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly`). Read `FEATURE_DIR`. The feature name is the folder name, for example `003-order-discount`. If the script is not available, use the current branch name.
2. Use the **qe-plan** skill for this feature. Pass the user input as the focus.
3. Next step for the user: `/speckit.tasks`, then `/speckit.testwrite`.
