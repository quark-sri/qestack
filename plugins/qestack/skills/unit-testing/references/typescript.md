# Unit testing recipe: TypeScript and JavaScript

Common stack: Vitest or Jest. Use what the project already has.

## Run a subset

- Vitest: `npx vitest run src/discount.test.ts -t "applies 10%"`
- Jest: `npx jest src/discount.test.ts -t "applies 10%"`

## Boundary set

```ts
test.each([
  { total: 99.99, expected: 99.99 },   // just below the limit
  { total: 100.0, expected: 90.0 },    // at the limit
  { total: 100.01, expected: 90.01 },  // just above
])('total $total -> $expected', ({ total, expected }) => {
  expect(applyDiscount(total)).toBeCloseTo(expected, 2);
});
```

## Errors: check the type AND the code or message

```ts
expect(() => applyDiscount(-0.01)).toThrowError(new RangeError('ORD-400'));
```

For async code: `await expect(service.apply(-1)).rejects.toThrow('ORD-400');` (do not forget `await`).

## Time and randomness

- Vitest: `vi.useFakeTimers(); vi.setSystemTime(new Date('2026-02-28T23:30:00Z'));` and `vi.useRealTimers()` after the test.
- Jest: `jest.useFakeTimers().setSystemTime(new Date('2026-02-28T23:30:00Z'));`
- Pass a random function or a seeded generator into the unit.

## Test doubles

- `vi.fn()` / `jest.fn()` for boundaries. `vi.mock('./rates')` only for modules at the boundary.
- Check the arguments of an important call: `expect(send).toHaveBeenCalledWith(expect.objectContaining({ orderId: 'o-1' }))`.

## Pitfalls

- A missing `await` makes an async test pass before the assertion runs.
- `toBeTruthy()` and `toBeDefined()` check almost nothing.
- Module-level state survives between tests in the same file. Reset it in `beforeEach`.
- Snapshot tests of computed values copy the current output, also when it is wrong.
