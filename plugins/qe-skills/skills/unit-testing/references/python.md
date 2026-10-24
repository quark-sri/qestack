# Unit testing recipe: Python

Common stack: pytest, with `unittest.mock` or `pytest-mock`. Use what the project already has.

## Run a subset

- One file or test: `pytest tests/test_discount.py::test_applies_discount -q`
- By name: `pytest -k "discount and not slow"`
- By marker: `@pytest.mark.fast`, then `pytest -m fast` (register markers in the pytest configuration)

## Boundary set

```python
@pytest.mark.parametrize(("total", "expected"), [
    (Decimal("99.99"), Decimal("99.99")),    # just below the limit
    (Decimal("100.00"), Decimal("90.00")),   # at the limit
    (Decimal("100.01"), Decimal("90.01")),   # just above
])
def test_applies_discount_from_one_hundred(total, expected):
    assert apply_discount(total) == expected
```

## Errors: check the type AND the code or message

```python
with pytest.raises(ValueError, match=r"^ORD-400$"):
    apply_discount(Decimal("-0.01"))
```

## Time and randomness

- Pass a clock function or a `datetime` into the unit. Or freeze time with a library such as `time-machine` or `freezegun`, if the project has one.
- Use `random.Random(42)` and pass it in, instead of the global `random`.

## Test doubles

- `mocker.patch("app.rates.current", return_value=Decimal("0.20"))` with pytest-mock, or `unittest.mock.patch`.
- Patch where the name is looked up (`app.service.rates`), not where it is defined.
- Check important call arguments: `send.assert_called_once_with(order_id="o-1", total=Decimal("90.00"))`.

## Pitfalls

- `float` money: `0.1 + 0.2 != 0.3`. Use `Decimal`, or `pytest.approx` with a stated tolerance.
- Fixtures with `scope="module"` or `"session"` share state between tests.
- A bare `assert result` checks only that the value is truthy.
