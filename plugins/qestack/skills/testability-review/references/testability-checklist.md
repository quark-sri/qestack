# Testability checklist

Score each factor for one behavior: 0 = blocked, 1 = possible but costly, 2 = easy. Write the evidence next to each score.

| Factor | Question | Typical seam when the score is 0 |
|---|---|---|
| Clock | Can a test set the current time and the time zone? | Pass a clock or a time source in |
| Randomness and identifiers | Can a test fix random values and generated IDs? | Pass a seeded source or an ID generator in |
| Network and services | Can a test replace each external call? | Interface at the boundary, with a fake |
| Files and environment | Can a test use its own folder, variables and settings? | Pass paths and settings in; no reads of global state |
| Global and static state | Does the behavior read or write a singleton or static field? | Pass the state in; reset it per test |
| Inputs | Can a test build every input with a small amount of setup? | Builders; smaller input types |
| Outputs | Can a test read the result from a return value or a public effect? | Return the result; do not only log or print it |
| Side effects | Can a test see each write, event and message? | Port or interface for each effect; a fake that records it |
| Errors | Are errors typed and visible, and not swallowed or only logged? | Return or throw a specific error |
| Concurrency | Can a test run the work in one thread and wait for the end? | Pass the executor in; return a handle to wait on |
| Size of the unit | Does one test need many collaborators? | Split by responsibility; narrow the interface |
| Observability in production | Do logs, metrics and IDs let a person find the cause of a failure? | Add the log, metric or correlation ID |

## Reading the total

- Mostly 2: write the tests at the unit level.
- Mixed with a few 0: fix the blockers first, or test at a higher level and say what is lost.
- Mostly 0 or 1 in the factors for the clock, state and effects: expect slow, flaky tests. Plan the seams before more tests.
