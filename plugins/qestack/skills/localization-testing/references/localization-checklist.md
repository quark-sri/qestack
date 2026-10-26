# Localization checklist

## Static checks

- Visible text in code, templates or images, instead of resource files.
- Text built by joining pieces ("Hello " + name + ", you have " + n + " items").
- Plural forms made with "if n == 1". Use the plural rules of the locale.
- Formatting calls with no locale, or with the machine default locale.
- Date, number and currency formats written by hand.
- Case changes and comparisons that ignore the locale (the Turkish dotted and dotless "i" is the classic case).
- Fixed widths, fixed heights and fixed field lengths for text.
- Images and icons that contain text, or that have a cultural meaning.

## Resource files

- Same set of keys in every locale. No empty values. No keys that the code does not use.
- Placeholders (names, counts) have the same names and number as the source.
- Plural and gender forms exist for every category that the locale needs (some locales have more than two plural forms).
- The fallback chain is defined (for example `de-CH` to `de` to the default) and tested.

## Pseudo-localization

Use a generated locale with accented letters, about 30% more length and visible markers at the start and the end of each text.

| Sign | Meaning |
|---|---|
| Text with no accents or markers | Hard-coded or not from the resource files |
| Marker cut off | Truncated text |
| Overlap or broken layout | Not enough room for longer languages |
| Garbled characters | An encoding problem |

## Formats

| Area | Check |
|---|---|
| Dates and times | Order and separators, 12 or 24 hours, first day of the week, calendar system, time zone and daylight saving time |
| Numbers | Decimal and group separators, digits, negative and percent forms |
| Currency | Symbol and position, decimals, rounding rules, the currency of the user and not of the locale |
| Sorting and search | The order of the locale, accents and case in search, natural order of numbers |
| Names and addresses | Order of given and family names, one-word names, long names, address lines, postal code and phone formats |
| Units | Metric or imperial, paper sizes, temperature |

## Text and data path

Use these values in every field that takes text, and check the stored, displayed, searched, sorted and exported result:

- Accented letters in two forms (one character, and letter plus combining mark). They must be treated as equal where the rule says so.
- Characters outside the basic plane (emoji, some Asian characters). Check length counts and truncation.
- Right-to-left text, and a mix of right-to-left and left-to-right text.
- A very long word with no spaces. Text longer than the field limit.
- Characters that need escaping in HTML, JSON, CSV, URLs and file names.

## Layout

- Expansion (German, Finnish, and others) in buttons, tables and menus. Contraction and tall scripts (Thai, Hindi) in line height.
- Right-to-left: mirrored layout, icons that show direction, progress bars, text alignment, numbers in the text.
- Fonts that have all needed characters. No missing-character boxes.
- The language of the page is set, so that screen readers and browsers choose the right rules.

## Region and legal rules

Ask the owner to confirm each item, and write the answer. Do not guess from the output.

- Tax and price display rules (prices with or without tax).
- Legal, privacy, consent and cookie text for the region.
- Required notices, age rules and contact data.
- Restrictions on content, maps, names of places and holidays.
- Payment methods, invoice formats and number formats on documents.
