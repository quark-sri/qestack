# Fault Catalog Rubric (seeded faults)

Version 1.0. The fault seeder follows these rules. The judge checks the catalog with them.

## A good seeded fault

1. **Realistic.** A developer could make this mistake. It is not random noise.
2. **Requirement-level.** It breaks one requirement ID that the spec states. The catalog names that ID.
3. **Observable.** The spec says what the correct behavior is, so a correct test can detect it.
4. **Compiles.** The code builds with the fault.
5. **Single.** One fault per patch.
6. **Not trivial.** Mutation testing already covers simple operator changes. Prefer semantic faults.

## Distribution

- 5 to 15 faults for each feature (see `loop.faults_min` / `faults_max`).
- At least one fault for each high-risk requirement.
- Cover each layer that the feature changes: domain rules, API, database, Kafka, UI.
- Mix the categories below.

## Categories

| Category | Examples |
|---|---|
| rule | Inverted condition, wrong rate, wrong rounding mode |
| boundary | `>` instead of `>=`, off-by-one in a limit |
| validation | Missing check of a required field, accepting a negative value |
| error-handling | Wrong error code, wrong HTTP status, swallowed exception |
| state | Missing save, wrong column, partial update, missing transaction |
| event | Missing publish, wrong key, missing header, duplicate publish, publish before commit |
| security | Missing role or tenant check |
| idempotency | Duplicate request creates a second record |

## Not allowed

- Faults that only change logging, comments or formatting.
- Faults in code that the feature did not touch, unless the feature depends on it.
- Faults that crash the whole application at startup (every test fails; this proves nothing).
- Faults that change the tests.

## Judge checks

The judge reviews `catalog.json` and the patches (in a separate seeder-review step), and reports:

- faults that are not realistic or not observable from the spec,
- requirement IDs with no fault,
- a catalog with only easy faults.
