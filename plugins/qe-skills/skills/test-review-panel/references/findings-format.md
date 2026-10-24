# Findings format

All reviewers return their findings in this format, and the lead writes the review folder from them. One format makes merging, comparing runs and pull request comments simple.

## What each reviewer returns

Each persona agent returns one message with two parts:

1. **The persona report** in the output format of the persona, for people.
2. **A findings block** at the end: one fenced JSON block. The "Reviewer rules" section of each persona agent defines its shape. The section is the same in all persona agents, and the validator checks this.

The lead checks each block with these rules:

| Field | Rule |
|---|---|
| `persona`, `scope` | The agent name and the scope of the brief |
| `tree_changed` | `true` if any file is different from the start. The lead stops the panel if it is `true` |
| `id` | The persona prefix and a number, for example `AB-1`, `HC-2`, `SB-3` |
| `severity` | `blocker`, `major` or `minor`, with the rules of the persona |
| `summary` | One sentence, at most 15 words |
| `evidence` | At least one `file` and `line`. A `quote` of the line when it helps. A finding with no evidence goes to `questions` |
| `scenario` | How the product can be wrong, slow or hard to change while the tests pass |
| `fix` | A concrete change. Never applied by the reviewer |
| `status` | `proven` (a run or a derivation shows it) or `suspected` |

Paths are relative to the repository root.

## What the lead writes

The lead writes one folder for each panel run. The default parent folder is `qa-reviews/`. The `Review reports` line of `.agents/qa-project-context.md` can change it.

```
qa-reviews/<YYYY-MM-DD>-<scope-slug>/
  panel-report.md        the merged, ranked findings and the verdict, for people
  findings.json          the same findings, machine-readable
  personas/<name>.md     the full message of each reviewer, unchanged
```

- `<scope-slug>`: lowercase letters, digits and hyphens, at most 40 characters, for example `pr-142` or `src-test-orders`. If the folder exists, add `-2`, `-3` and so on. Never overwrite an earlier run.
- `personas/<name>.md` keeps the reviewer message as it came, so that a person can check the lead.

`findings.json` has this shape:

```json
{
  "scope": "src/test/orders",
  "date": "2026-10-24",
  "commit": "108e9c0",
  "panel": ["domain-oracle-reviewer", "saboteur"],
  "independent": true,
  "tree_restored": true,
  "verdict": "ready-after-fixes",
  "counts": { "blocker": 1, "major": 0, "minor": 0, "rejected": 0 },
  "findings": [
    {
      "rank": 1,
      "severity": "blocker",
      "summary": "Boundary at 100.00 expects no discount, and the fault survives",
      "evidence": [
        { "file": "src/test/orders/DiscountTest.java", "line": 31 },
        { "file": "src/main/orders/Discount.java", "line": 27 }
      ],
      "scenario": "Rule R3 gives 10% off at 100.00 or more",
      "fix": "Expect 90.00 at exactly 100.00",
      "found_by": ["domain-oracle-reviewer", "saboteur"],
      "source_ids": ["DO-1", "SB-1"],
      "lead_check": "accepted"
    }
  ],
  "rejected": [{ "source_id": "MC-4", "reason": "The value is named in the builder; no mystery data" }],
  "questions": ["Rule R5 is silent about refunds after 30 days"]
}
```

- `verdict`: `ready`, `ready-after-fixes` or `not-ready`.
- `lead_check`: `accepted` after the lead opened the evidence. Blockers and major findings must have it.
- Keep `found_by` and `source_ids` in the same order, so that each merged finding points back to the persona reports.

## If a reviewer returns no findings block

Do not guess the fields. Ask the reviewer once to return the block. If it does not, take the findings from its persona report by hand, and add a line about this to `panel-report.md`.
