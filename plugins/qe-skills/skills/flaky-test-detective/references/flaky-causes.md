# Catalog of flaky causes

| Category | Signs in the test or the code | Real fix |
|---|---|---|
| Fixed wait | A sleep, a fixed delay, "wait 2 seconds" | Wait for a condition (poll with a timeout) |
| Asynchronous work | The test asserts before a background job, a message or a UI update has finished | Wait for the observable result, or make the work synchronous in the test |
| Order dependence | Passes alone, fails after another test (or the reverse) | Each test creates and cleans its own data; no shared state |
| Shared mutable state | Static or global variables, singletons, caches, shared files, a shared database row | Reset the state in setup, or use unique data for each test |
| Test data collisions | Fixed IDs, names or emails; parallel tests use the same data | Unique data for each test (generated with a seed) |
| Time | The real clock, "today", time zones, daylight saving, end of month, a timeout close to the real duration | Inject a fixed clock; set the time zone; use relative and generous limits only with a reason |
| Randomness | Random data without a fixed seed | A fixed seed; log the seed on failure |
| Unordered collections | Asserts on the order of a set, a map or a query without an order | Sort before you compare, or compare without order |
| Concurrency | Threads, parallel requests, locks, connection pools | A deterministic test setup; a real fix in the code when it is a product race |
| Resource leaks | Open files, connections, ports or threads from earlier tests | Close resources in cleanup; use free ports |
| Environment | Locale, encoding, file paths, line endings, CPU speed, memory, another version of a tool or runtime | Set the environment explicitly; pin versions |
| External services | A real network call, a third-party API, a shared test environment | Replace with a local fake or a container at the boundary |
| Floating point | Exact comparison of floating point results | Compare with a tolerance, or use decimal types |
| Retries in the framework | A rerun setting hides failures | Turn reruns off while you investigate |
| Test framework misuse | Assertions in callbacks that never run; a missing await; a test that ends before its async work | Await the work; assert that the callback ran |
