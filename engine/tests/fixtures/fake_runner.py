"""Simulates a test run: writes Surefire-style JUnit XML for GoodDiscountTest.
A test passes only if the production code implements its rule."""
import os
import pathlib
import sys

src = pathlib.Path("src/main/java/com/acme/order/Discount.java").read_text()
impl = "total * 0.9" in src and ">= 100.0" in src
cases = {
    "discountAtThreshold": impl,
    "noDiscountBelow": impl,
    "negativeTotalOnlyNotNull": "total < 0" in src and '"ORD-400"' in src,
}
os.makedirs("target/surefire-reports", exist_ok=True)
xml = ['<testsuite name="com.acme.order.DiscountTest">']
for k, ok in cases.items():
    xml.append(f'<testcase classname="com.acme.order.DiscountTest" name="{k}()">' + ("" if ok else "<failure/>") + "</testcase>")
xml.append("</testsuite>")
pathlib.Path("target/surefire-reports/TEST-com.acme.order.DiscountTest.xml").write_text("\n".join(xml))
sys.exit(0 if all(cases.values()) else 1)
