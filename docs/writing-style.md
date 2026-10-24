# Writing style: Simplified Technical English

All qestack documentation, skills, agent prompts, rubrics and command-line messages use Simplified Technical English (STE). STE is based on the ASD-STE100 standard. It makes text clear for readers who use English as a second language, and for AI agents.

## Why STE for agent prompts

An agent follows the words that you write. Short, direct sentences give fewer wrong interpretations. One instruction in each sentence makes each rule easy to check.

## Rules

### Words

1. Use common words. Write "use", not "utilize". Write "start", not "initiate". Write "help", not "facilitate".
2. Use one word for one meaning. When you choose a term, keep it. In qestack: "stack", "ruleset", "gate", "judge", "lock", "feature", "requirement ID".
3. Use technical names as they are: `qestack lint`, `@Tag`, `pom.xml`, "mutation score".
4. Do not use slang, idioms or metaphors.

### Sentences

5. Keep procedural sentences short: 20 words or fewer.
6. Keep descriptive sentences short: 25 words or fewer.
7. Write one instruction in each sentence.
8. Use the active voice. Write "The engine writes the report", not "The report is written".
9. Write instructions in the imperative. Write "Run `qestack doctor`", not "You should run `qestack doctor`".
10. Put a condition before the instruction. Write "If the gate fails, read the report."

### Structure

11. Use numbered lists for steps that have an order.
12. Use bullet lists for items without an order.
13. Use tables for rules, options and comparisons.
14. Write one topic in each paragraph. Keep paragraphs to 4 sentences or fewer.

### Agent prompts

15. Start with the role: "You are the qestack test judge."
16. Give a "Forbidden" section with explicit "Do not" rules.
17. Give a numbered "Procedure".
18. Tell the agent what to reply. Ask for counts and summaries, not for pasted files.
19. Use MUST and NOT in capitals only for the most important rules.

## Examples

| Not this | This |
|---|---|
| It is recommended that the user should consider configuring the assertion helpers in order to avoid potential false positives. | Register your assertion helpers. Without them, the lint gate reports false findings. |
| The test may be weakened by the agent if the hook is not installed. | Install the hook. Without the hook, an agent can weaken locked tests. |
| Leverage mutation testing to holistically assess suite robustness. | Use mutation testing. It shows which code changes no test detects. |

## Check your text

- Is each sentence 20 to 25 words or fewer?
- Does each sentence have one idea?
- Is each verb active?
- Did you use the same term for the same thing?
