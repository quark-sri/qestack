# Localization testing recipe: Python

Common stack: `babel` for formats, `gettext` or the framework's translation for messages. Use what the project already has.

## Always pass the locale, and fix it in the test

Do not use the process locale (`locale.setlocale`). It is global state. Pass the locale to the function.

```python
@pytest.mark.parametrize(("loc", "expected"), [
    ("de_DE", "1.234.567,89"),
    ("en_US", "1,234,567.89"),
    ("en_IN", "12,34,567.89"),
])
def test_formats_number(loc, expected):
    assert numbers.format_decimal(1234567.89, locale=loc) == expected   # from babel import numbers
```

The locale data depends on the version of the library. Take expected values from the requirement or the market owner, and pin the version.

## Dates and time zones

Use time-zone-aware values (`zoneinfo`). Test the day of a clock change and the end of the month. Never use a naive `datetime.now()` in a test.

## Message files

One test loads each catalog, compares the key set with the base catalog, compares the placeholders, and checks the plural forms for the locale. Fail on a missing or empty message.

## Hard characters

```python
samples = ["é", "é", "👩🏽‍💻", "שלום world", "a" * 300]
assert unicodedata.normalize("NFC", samples[0]) == unicodedata.normalize("NFC", samples[1])
```

Send each sample through the form, the API, the database and the export. Compare the result with the input. Check the length rules: `len()` counts code points, not what the user sees.
