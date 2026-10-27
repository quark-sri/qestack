---
description: "Neighbor check: an intermittent CI failure starts flaky-test-detective, not test-runner or test-environments."
tags: [routing]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

This test passes on my machine but fails about once in ten runs in CI. Find out why.

```java
@Test
void expiresAfterOneDay() throws Exception {
    var token = tokens.create(user);
    Thread.sleep(50);
    assertEquals(LocalDate.now().plusDays(1), token.expiry());
}
```
