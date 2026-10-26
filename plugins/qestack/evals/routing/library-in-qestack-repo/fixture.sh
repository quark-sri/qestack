#!/usr/bin/env bash
# Workspace for case library-in-qestack-repo: a qestack repository with one weak test class.
set -euo pipefail
mkdir -p .qestack src/test/java/com/acme/order
cat > .qestack/project.toml <<'EOF'
[project]
stack = "java-maven-junit5"
EOF
cat > src/test/java/com/acme/order/DiscountTest.java <<'EOF'
package com.acme.order;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class DiscountTest {
    private final Discount d = new Discount();

    @Test
    void discountAtThreshold() { assertEquals(90.0, d.apply(100.0), 0.001); }

    @Test
    void hollowTest() { }

    @Disabled("flaky")
    @Test
    void skipped() { assertEquals(1, 1); }
}
EOF
