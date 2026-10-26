---
name: localization-testing
description: "Tests internationalization and localization: hard-coded text, pseudo-localization, translations, plurals, dates, numbers, currency, Unicode, right-to-left layout and locale fallback. Use when the user says 'i18n test', 'localization test' or 'right-to-left'. Not for accessibility (use accessibility-testing)."
argument-hint: "[feature, screen, locale list or release region]"
---

# localization-testing

## Objective

A product that works in one locale often breaks in another: truncated text, wrong dates, broken sorting, unreadable characters, missing legal text. This skill finds those defects early. It checks that the code supports many locales (internationalization), and that each supported locale is correct (localization).

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its markets, UI test framework, quality goals and risks.
2. If it does not exist, find the locale files and the formatting code in the repository. Suggest `qa-project-context` once.

## Discovery questions

1. Which locales and regions are supported now, and which are planned? Which are the highest risk (right-to-left, long text, non-Latin scripts, different calendars)?
2. Where do the texts come from (resource files, a translation service, the database)? Who translates and reviews?
3. Which formats and rules depend on the region: dates, numbers, currency, taxes, addresses, names, phone numbers, legal and privacy text?
4. Which standards must hold (Unicode, locale tags, the message format used by the project)?

## Principles

1. **Separate the text from the code.** No visible text, format or rule is hard-coded. Find the exceptions first, they are the cheapest defects.
2. **Use the platform's locale rules,** not hand-written formats. Test that every format takes the locale as input, never the machine default.
3. **Pseudo-localization before translation.** Accented, longer text with markers shows hard-coded text, truncation and broken layout without a translator.
4. **The locale is not the language.** Test the region (German in Germany and Switzerland), the script and the fallback chain.
5. **A native reader checks meaning.** Automated tests check structure, placeholders and layout. A person checks that the translation is correct and natural.
6. **Money and legal rules are domain rules.** Get the expected values from the requirement or the legal owner, not from the output.

## Workflow

1. List the locales, the screens and the data that depend on the locale. Rank them by risk.
2. Scan for hard-coded text and for formats that use the default locale (see [the checklist](references/localization-checklist.md), section "Static checks").
3. Run the product in pseudo-locale. Look for untranslated text, truncated text, broken layout and text built by joining pieces.
4. Check each resource file: no missing keys, no extra keys, placeholders and plural forms match the source, no empty values.
5. Test the formats for each target locale with exact expected values (the stack recipe has examples): dates and time zones, numbers, currency, sorting, search, and case rules.
6. Test the data path with hard characters: accents, combined characters, emoji, long names, right-to-left text, and text that is longer than the field. Check that it is stored, shown, searched and exported with no change.
7. Test the layout in the widest and the right-to-left locales: expansion, mirroring, icons, mixed-direction text.
8. Check the region rules: address and phone forms, legal and privacy text, tax and currency rules, consent text. Mark each as confirmed by the owner, or as a question.
9. Report each defect with the locale, the screen or data, the expected result, the actual result and the fix. Add the regression test.

## Stack recipes

Read only the recipe for the stack of the project: [Java](references/java.md), [TypeScript and JavaScript](references/typescript.md), [Python](references/python.md). For another stack, apply the principles with the project's own libraries, and say so.

## Anti-patterns

- **Testing only English and one translated language.**
- **The default locale of the build machine decides the result.** The test passes in one place and fails in another.
- **Text built by joining pieces,** which breaks in languages with a different word order.
- **Formatting numbers and dates by hand.**
- **Expected values copied from the output.** A wrong format then passes.
- **Machine translation shipped with no native review** of legal, safety or payment text.

## Done when

- Each supported locale has been run in the product, with the highest-risk ones checked in the layout.
- Resource files have no missing keys, and the placeholders and plurals match.
- The formats of each locale are tested with exact expected values and a fixed locale, not the machine default.
- Hard characters pass through the data path with no change.
- Region rules are confirmed by their owner or listed as open questions.

## Related skills

- `ui-automation`: runs the layout and text checks in the browser.
- `edge-case-hunter`: more cases for text, dates and numbers.
- `accessibility-testing`: language tags and screen reader behavior per locale.
- `test-data-management`: data with realistic names, addresses and scripts.
