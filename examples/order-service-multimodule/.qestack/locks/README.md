# qestack locks and human decisions

This folder is protected. Agents cannot edit it (hook and CI guard). Commit it to git.

| File | Written by | Meaning |
|---|---|---|
| `<feature>.json` | `qestack lock` | Snapshot of the approved tests. Later edits must not weaken them. `qestack lock` refuses a weakening update. Only a human may run `qestack lock --force`. |
| `<feature>.equivalent.json` | Human | Surviving mutants that cannot change behavior. Format: `[{"file": "src/main/java/.../X.java", "line": 42, "mutator": "ConditionalsBoundaryMutator", "reason": "..."}]` |
| `<feature>.red-exempt.json` | Human | Test keys that may pass before the implementation (the behavior existed before). Format: `["src/test/java/...::Class.method"]` |

Review every change to this folder in code review (CODEOWNERS).
