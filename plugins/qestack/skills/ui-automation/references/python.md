# UI automation recipe: Python

Common choices: Playwright for Python with the pytest plugin, or Selenium WebDriver. Use what the project already has.

## Playwright for Python (pytest)

```python
from playwright.sync_api import Page, expect

def test_buyer_pays_order(page: Page, api, base_url):
    order_no = api.create_order_for("buyer")                       # set up through the API
    page.goto(f"{base_url}/orders/{order_no}")
    page.get_by_role("button", name="Pay now").click()
    expect(page.get_by_role("heading", name="Payment received")).to_be_visible()
    expect(page.get_by_test_id("order-status")).to_have_text("PAID")   # retrying assertion
    assert api.order_status(order_no) == "PAID"
```

- Run with traces for failures: `pytest --tracing retain-on-failure --screenshot only-on-failure`.
- Reuse a logged-in state: save `storage_state` once and pass it to new contexts.

## Selenium WebDriver

- Use `WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "[data-testid=order-status]"), "PAID"))`.
- Do not use `time.sleep`.
- Save a screenshot in a pytest hook when a test fails.
