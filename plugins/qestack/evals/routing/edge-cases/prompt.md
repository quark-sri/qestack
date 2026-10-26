---
description: "Session test S3: a request for missing edge cases in a spec starts edge-case-hunter or requirement-gaps."
tags: [routing]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

What edge cases are missing in this spec?

```markdown
# Feature 001: order discount

- FR-001: An order total of 100.00 or more gets a 10% discount.
- FR-002: A negative order total is rejected with an error.
- FR-003: The discount is shown on the order confirmation.
```
