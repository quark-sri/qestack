# Accessibility testing recipe: TypeScript and JavaScript

Common choices: `@axe-core/playwright` with Playwright Test, `cypress-axe` with Cypress, `jest-axe` or `vitest-axe` for component tests. Use what the project already has.

## Playwright Test with axe

```ts
import AxeBuilder from '@axe-core/playwright';

test('checkout has no serious accessibility violations', async ({ page }) => {
  await page.goto('/checkout');
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  const serious = results.violations.filter((v) => ['serious', 'critical'].includes(v.impact ?? ''));
  expect(serious, JSON.stringify(serious.map((v) => [v.id, v.nodes.length]))).toEqual([]);
});
```

Analyze again after state changes: `await page.getByRole('button', { name: 'Pay now' }).click();` with an invalid card, then analyze the error state.

## Component tests

`jest-axe`: `expect(await axe(container)).toHaveNoViolations();` for each component state.

## Keyboard checks in tests

`await page.keyboard.press('Tab'); await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();`
