# Localization testing recipe: Java

Common stack: `java.text`, `java.time.format` and `ResourceBundle`, or the message source of the framework. ICU4J when the project already uses it.

## Always pass the locale, and fix it in the test

Never rely on `Locale.getDefault()`. Set the locale in the code under test as a parameter. If you must set the default, restore it after the test.

```java
@ParameterizedTest
@CsvSource(delimiter = '|', value = {"de-DE|1.234.567,89", "en-US|1,234,567.89", "en-IN|12,34,567.89"})
void formatsNumbersByLocale(String tag, String expected) {
    NumberFormat f = NumberFormat.getNumberInstance(Locale.forLanguageTag(tag));
    f.setMinimumFractionDigits(2);
    assertEquals(expected, f.format(1234567.89));
}
```

The data comes from the CLDR data of the JDK, which can differ between versions (for example, the kind of space in French). Take the expected values from the requirement or the market owner, and pin the JDK version in the build.

## Dates and time zones

```java
ZonedDateTime t = ZonedDateTime.of(2026, 3, 29, 1, 30, 0, 0, ZoneId.of("Europe/Berlin"));  // day of a clock change
assertEquals("29.03.2026", DateTimeFormatter.ofLocalizedDate(FormatStyle.MEDIUM).withLocale(Locale.GERMANY).format(t));
```

Test the days of a clock change, the end of the month and the end of the year.

## Resource files

Load each bundle for every supported locale in one test. Compare the key sets with the base bundle, and compare the placeholders (`{0}`, `{1}` or named ones) for each key. Fail on a missing key.

## Case rules

`"title".toUpperCase(Locale.forLanguageTag("tr"))` gives a dotted capital "İ". Test the case rules with the locale argument, and look for calls that omit it.
