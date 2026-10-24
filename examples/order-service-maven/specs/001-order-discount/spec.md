# Feature Specification: Order discount

### User Story 1 - Customer gets a discount (Priority: P1)

A customer checks out an order. Large orders get a discount, and the system tells other services about it.

**Independent Test**: check out orders below, at and above the limit, and check the total and the event.

**Acceptance Scenarios**:

1. **Given** an order ORD-1 of 100.00, **When** the customer checks out, **Then** the total is 90.00 and an OrderDiscounted event with key ORD-1 is published.
2. **Given** an order of 99.99, **When** the customer checks out, **Then** the total is 99.99 and no event is published.
3. **Given** an order of -1.00, **When** the customer checks out, **Then** the checkout is rejected with error code ORD-400 and no event is published.

---

### Edge Cases

- A total of exactly 0.00 is valid. It gets no discount.
- Totals have two decimal places. The discount rounds half up to two decimal places (for example 100.05 becomes 90.05, from 90.045).

## Requirements

### Functional Requirements

- **FR-001**: System MUST apply a 10% discount when the order total is 100.00 or more. The result has two decimal places, rounded half up.
- **FR-002**: System MUST reject an order with a negative total with error code ORD-400.
- **FR-003**: System MUST publish one OrderDiscounted event, with the order ID as the key and the discounted total, when a discount applies. It MUST NOT publish an event when no discount applies or the order is rejected.
