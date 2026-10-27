---
description: "Over-trigger check: a general coding request that is not about testing starts no qestack skill."
tags: [routing]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename the variable `tmp` to `orderTotal` in this method and make it easier to read.

```java
double calc(List<Item> items) {
    double tmp = 0;
    for (Item i : items) { tmp = tmp + i.price() * i.qty(); }
    return tmp;
}
```
