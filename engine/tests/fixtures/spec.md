# Feature Specification: Order discount

### User Story 1 - Customer gets a discount (Priority: P1)

**Independent Test**: ...

**Acceptance Scenarios**:

1. **Given** an order of 100.00, **When** the customer checks out, **Then** a 10% discount is applied.
2. **Given** an order of 99.99, **When** the customer checks out, **Then** no discount is applied.

---

### Edge Cases

- What happens when the total is negative?

## Requirements

### Functional Requirements

- **FR-001**: System MUST apply a 10% discount when the order total is 100.00 or more.
- **FR-002**: System MUST reject orders with a negative total with error code ORD-400.
- **FR-003**: System MUST publish an OrderDiscounted event to Kafka. [NEEDS CLARIFICATION: key?]

### Success Criteria
- **SC-001**: 95% of checkouts complete in 1s.
