# Test design techniques

Choose the technique from the shape of the rule.

| Rule shape | Technique |
|---|---|
| An input with valid and invalid ranges or groups | Equivalence classes + boundary values |
| A result that depends on two or more conditions | Decision table |
| An object with a status or a life cycle | State transition |
| Many parameters with a few values each | Pairwise (all pairs) |
| A calculation | Equivalence classes + boundary values + known examples |
| A sequence of user steps | Use case / scenario paths |
| Areas where defects often hide | Error guessing with a checklist |

## Equivalence classes

1. Split each input into classes. The system treats all values in one class the same way.
2. Make at least one valid class and each invalid class (wrong type, out of range, missing, wrong format).
3. Take one value from each class. Do not combine two invalid classes in one case: the first error hides the second.

## Boundary values

1. For each limit, test the limit itself, one step below and one step above.
2. The step comes from the data type: 1 for integers, 0.01 for money with two decimals, 1 day, 1 second, 1 character.
3. Also test the limits of the type: zero, empty, the largest value.
4. Check that the requirement says if the limit is included. If not, it is a question.

## Decision tables

1. List the conditions (for example "member", "total ≥ 100", "coupon valid").
2. List the actions or results.
3. Make one column for each combination that changes the result. Merge columns where a condition does not matter ("-").
4. Each column becomes one test case.

| Conditions / results | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| member | Y | Y | N | N |
| total ≥ 100 | Y | N | Y | N |
| discount | 15% | 5% | 10% | 0% |

## State transitions

1. Draw the states and the events that move between them.
2. Test each valid transition once.
3. Test each invalid transition (an event in a state where it is not allowed). The expected result is a rejection, and the state does not change.
4. For high risk, test sequences: create, pay, cancel, refund.

## Pairwise

1. Use pairwise when the full combination of parameters is too large (for example browser × locale × role × plan).
2. Each pair of values appears in at least one case. This finds most defects that come from two interacting parameters.
3. Add the high-risk combinations by hand.

## Error guessing

Use a checklist of known defect areas: empty and null, zero, duplicates, time zones, rounding, concurrency, retries, permissions, very large data, special characters, partial failures.

## Test levels

| Level | Use for | Avoid for |
|---|---|---|
| Unit | Business rules, calculations, validation, mapping | Wiring, real infrastructure |
| Component / API | The contract of one service: status, body, errors, auth | UI behavior |
| Integration | Real database, queue, cache, file system effects | Pure logic |
| Contract | The agreement between a consumer and a provider | Business rules |
| End-to-end / UI | A few critical user journeys | Each rule and each edge case |
