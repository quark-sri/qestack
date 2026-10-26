# Gap checklist for one requirement

| Area | Gap to find |
|---|---|
| Example | No concrete example with input and expected output |
| Limits | A number, length, size, date or count with no limit, or a limit that does not say if it is included ("over 100": is 100 in?) |
| Units and precision | Money without currency or rounding rule; time without time zone; size without unit |
| Errors | Invalid input with no defined result (message, code, status, state after the error) |
| Effects | It does not say what is saved, sent or changed, and what must NOT change on failure |
| States | A status field with no list of allowed transitions |
| Actors | No actor, or "the system" acts with no trigger |
| Permissions | No rule for who may do it and who may not |
| Vague words | "fast", "easy", "user-friendly", "appropriate", "some", "etc.", "and/or", "should" (is it a must?) |
| Defaults | An optional input with no default value |
| Concurrency | Two users or two requests at the same time, with no rule |
| Time | Expiry, scheduling, daylight saving, end of month, leap year, with no rule |
| Data | Empty, null, duplicate, very large, special characters, other languages, with no rule |
| Integrations | A call to another system with no rule for a timeout, an error or a duplicate |
| Non-functional | A response time, a volume, an availability or an accessibility need that the domain implies but the text does not state |
| Testability | A statement that no test can check ("the code is clean", "works well") |
