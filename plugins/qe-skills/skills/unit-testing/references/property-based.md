# Property-based testing

An example test checks one input. A property test states a rule that must hold for all valid inputs, and the tool tries many generated inputs. When a case fails, the tool shrinks it to a small input.

## When to use it

- Parsers, formatters and converters: encode then decode returns the original (round trip).
- Calculations with invariants: the total equals the sum of the parts, a discount never makes the price negative.
- Sorting, merging and collections: the result is ordered, has the same elements, and sorting twice changes nothing (idempotence).
- State machines: any valid sequence of actions keeps the invariants.
- Two implementations of the same rule: the new one gives the same answer as the simple, slow one.

Keep example tests for the rules from the requirement. A property does not replace them. It finds the cases that nobody listed.

## How to write a property

1. State the rule in one sentence, from the requirement. Do not copy the formula under test, or a shared defect passes.
2. Describe the valid inputs with generators, and narrow them to the real domain (money has two decimals, IDs have a format).
3. Assert the rule, not an exact output. Use round trips, invariants, idempotence, and a comparison with a simple reference.
4. Keep the seed. When a property fails, copy the seed and the shrunk input into a normal example test as a regression test.
5. Keep the run fast: about 100 cases in the pipeline. Run more on a schedule.

## Pitfalls

- **A generator that never produces the hard cases.** Add the edge values (zero, empty, maximum, negative, Unicode) as explicit examples.
- **A property that is always true.** Break the code on purpose, and check that the property fails (see `mutation-probe`).
- **Filtering with many rejected inputs.** Build valid values directly instead of discarding most of them.
- **Random without a seed,** which makes a failure impossible to repeat.

## Recipes

Use the library that the project already has. Common choices:

| Stack | Library |
|---|---|
| Java | jqwik |
| TypeScript and JavaScript | fast-check |
| Python | Hypothesis |

### Java (jqwik)

```java
@Property
void discountNeverGivesNegativePrice(@ForAll @BigRange(min = "0.00", max = "100000.00") @Scale(2) BigDecimal total) {
    assertTrue(applyDiscount(total).signum() >= 0);
}
```

### TypeScript (fast-check)

```ts
import fc from 'fast-check';

test('encode then decode returns the input', () => {
  fc.assert(fc.property(fc.string(), (s) => decode(encode(s)) === s));
});
```

On failure, `fast-check` prints the seed and the shrunk input. Pass `{ seed, path }` to repeat the run.

### Python (Hypothesis)

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_encode_then_decode_returns_input(s):
    assert decode(encode(s)) == s
```

Hypothesis keeps failing cases in a local database and repeats them. Commit the shrunk case as an `@example(...)` so that it runs on every machine.
