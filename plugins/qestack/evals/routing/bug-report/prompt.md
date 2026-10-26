---
description: "Neighbor check: a known failure to write up starts bug-report, not bug-hunter."
tags: [routing]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Turn this failure into a bug report for the team.

```
POST /orders with total=-1 returned 201 Created (expected 400).
org.opentest4j.AssertionFailedError: expected: <400> but was: <201>
    at OrderApiTest.rejectsNegativeTotal(OrderApiTest.java:42)
```
