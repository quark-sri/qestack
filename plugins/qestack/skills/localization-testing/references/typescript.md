# Localization testing recipe: TypeScript and JavaScript

Common stack: the built-in `Intl` API, and the project's i18n library (for example i18next, FormatJS or the framework's own).

## Always pass the locale, and fix it in the test

```ts
test.each([
  ['de-DE', '1.234.567,89'],
  ['en-US', '1,234,567.89'],
  ['en-IN', '12,34,567.89'],
])('formats the number for %s', (locale, expected) => {
  expect(new Intl.NumberFormat(locale, { minimumFractionDigits: 2 }).format(1234567.89)).toBe(expected);
});
```

`Intl` data depends on the Node and browser version. Take expected values from the requirement or the market owner, and pin the Node version in CI. Set the time zone for the test run with the `TZ` environment variable, and test a clock-change day.

## Resource files

One test loads all locale files, compares the key sets with the base file, and compares the placeholders of each key. Check plural forms with `new Intl.PluralRules(locale).resolvedOptions().pluralCategories`: each category must have a text.

## Browser tests

Run the UI tests with a locale and a time zone for the context (for example Playwright `locale` and `timezoneId` options). Add a pseudo-locale build, and take a screenshot only to review it by eye, not as an exact comparison. For right-to-left, set `dir="rtl"` and check the layout and the focus order.

## Hard characters

```ts
const samples = ['é', 'é', '👩🏽‍💻', 'שלום world', 'a'.repeat(300)];
```

Send each sample through the form, the API and the export, and compare the result with the input.
