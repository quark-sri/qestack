# UI automation recipe: TypeScript and JavaScript

Common choices: Playwright Test, or Cypress. Use what the project already has.

## Playwright Test

```ts
test('TC-021: a buyer can pay an order and sees the confirmation', async ({ page, request }) => {
  const orderNo = await createOrderFor(request, 'buyer');            // set up through the API
  await page.goto(`/orders/${orderNo}`);
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByRole('heading', { name: 'Payment received' })).toBeVisible();
  await expect(page.getByTestId('order-status')).toHaveText('PAID');  // retrying assertion
  expect(await orderStatus(request, orderNo)).toBe('PAID');
});
```

- Log in once in a setup project and save `storageState`; tests then start logged in.
- In the configuration: `use: { trace: 'retain-on-failure', screenshot: 'only-on-failure' }`.
- Keep `retries` at 0 while you investigate instability; a retry hides it.
- Page objects return locators and perform actions; the test keeps the business assertions.

## Cypress

- Use `cy.findByRole` (Testing Library) or `[data-cy=...]` selectors.
- Cypress commands retry; do not add `cy.wait(<ms>)`. Wait for a request alias or an assertion instead.
- Set up data with `cy.request` or a task, not through the UI.
