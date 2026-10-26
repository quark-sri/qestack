# Mutation testing recipe: TypeScript and JavaScript

Common choice: StrykerJS with the runner plugin for the project's test framework (Vitest, Jest or Mocha). Use what the project already has.

## One file

```
npx stryker run --mutate "src/discount.ts"
```

Configure `stryker.config.json` (or `.mjs`) with `testRunner` (for example `vitest` or `jest`), `reporters: ["html", "json", "clear-text"]`, and `coverageAnalysis: "perTest"`.

## Reading the report

- `Survived`: a test ran the code and did not notice the change.
- `NoCoverage`: no test ran the code.
- `Killed`, `Timeout`: detected.

The JSON report is in `reports/mutation/mutation.json`; the HTML report shows each mutant in the source.

## Tips

- Use `--incremental` for repeated runs.
- Run end-to-end tests outside the mutation run; they are too slow for it.
