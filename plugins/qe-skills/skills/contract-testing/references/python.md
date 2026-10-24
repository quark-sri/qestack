# Contract testing recipe: Python

Common choice: Pact Python (`pact-python`) with a Pact Broker. Check the API for the installed major version: version 3 changed the interface. Use what the project already has.

## Consumer test (shape)

1. Create a Pact for the consumer and the provider.
2. Declare the interaction: the provider state ("order ORD-1 exists"), the request (`GET /orders/ORD-1`), and the response with matchers (a type matcher for `total`, a regex for `status`).
3. Run the consumer's client code against the mock server that Pact starts, and assert on what the client returns.
4. Pact writes the contract file. Publish it to the broker with the consumer version and branch.

## Provider verification

Run the Pact verifier against the provider's test instance, with the broker as the source and a provider-state endpoint or hook that creates the data for each state.

## Events

For events with a schema registry: set the compatibility mode for each subject and check new schemas against the registry in the pipeline before you publish.

## Pitfalls

- A contract written by the provider team does not show what consumers need.
- Exact values everywhere make the contract fragile. Use matchers.
