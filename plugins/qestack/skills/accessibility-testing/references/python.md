# Accessibility testing recipe: Python

Common choices: an axe integration for Playwright for Python (for example `axe-playwright-python`) or for Selenium (for example `axe-selenium-python`). Check the package and its API in the project.

## Playwright for Python with axe (shape)

```python
def test_checkout_has_no_serious_violations(page, base_url):
    page.goto(f"{base_url}/checkout")
    results = run_axe(page, tags=["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])   # project helper around the axe package
    serious = [v for v in results["violations"] if v["impact"] in ("serious", "critical")]
    assert serious == [], [(v["id"], len(v["nodes"])) for v in serious]
```

A small helper can also inject the axe-core script into the page and call `axe.run()` with `page.evaluate`, if no package is available.

## Keyboard checks

`page.keyboard.press("Tab")`, then `expect(page.get_by_role("link", name="Skip to content")).to_be_focused()`.
