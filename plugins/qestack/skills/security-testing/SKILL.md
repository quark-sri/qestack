---
name: security-testing
description: "Plans and writes security tests for an application or API: authentication, authorization and object access, injection, data exposure, headers, secrets, rate limits and business logic abuse. Use when the user says 'security test', 'OWASP', 'pen test checklist' or asks 'can users see other users data'. Not for a specialist penetration test."
argument-hint: "[application, API, feature or change]"
---

# security-testing

## Objective

Most security defects are ordinary bugs in access checks, input handling and configuration. Functional tests rarely look for them because they test what users should do, not what attackers try. This skill adds tests for what must NOT be possible, and puts automatic scans in the pipeline. It does not replace a specialist penetration test.

## Context

1. Read `.agents/qa-project-context.md` if it exists. Use its tech stack, roles, environments and risk areas.
2. If it does not exist, find the roles, the endpoints and the authentication method in the code and the configuration. Suggest `qa-project-context` once.

## Discovery questions

1. Which data is sensitive (personal data, payment data, secrets, health data)?
2. Which roles and tenants exist, and what may each one do?
3. How do users authenticate, and how do services authenticate to each other?
4. Which environment may receive security tests? Is written permission needed?

## Principles

1. **Test only with permission,** and only in environments that the owner approves.
2. **Negative tests are the core:** another user's object, a missing role, a forged token, a changed price, an injection string.
3. **Every access rule is a test.** For each endpoint and each object type: who may read, change and delete.
4. **Automate the repeatable checks** (dependency scan, secret scan, header checks, scanner baseline) in the pipeline. Use manual exploration for logic abuse.
5. **No real secrets or personal data** in tests, logs or reports.

## Workflow

1. Map the attack surface: entry points, roles, sensitive data, trust boundaries, external calls.
2. For each area of [the security checklist](references/security-checklist.md) that applies, design the tests.
3. Write the access tests first: for each endpoint and role, the allowed and the forbidden calls, and the objects of another owner.
4. Write the input tests: injection strings for each input that reaches a query, a command, a template, a path or a page; oversized and malformed input.
5. Check the responses and logs for sensitive data: errors without stack traces, no tokens or personal data in logs.
6. Add the pipeline scans: dependencies with known vulnerabilities, committed secrets, a baseline scan of the running application.
7. Report each finding with the steps, the evidence, the impact and a severity. Tell the owner before you share it widely.

## Anti-patterns

- **Scanner output as the result.** A clean scan does not prove that access rules are right.
- **Only the happy path for authentication.** The forbidden cases are the security tests.
- **Testing production without permission.**
- **Real credentials in test code.**

## Done when

- Each endpoint in scope has tests for the forbidden roles and for another owner's objects.
- Each input that reaches a query, command, template, path or page has injection tests.
- Sensitive data does not appear in errors, logs or responses where it must not.
- Dependency, secret and baseline scans run in the pipeline.
- The findings are reported with evidence and severity to the owner.

## Related skills

- `api-testing`: the authorization and error cases of each endpoint.
- `bug-hunter`: security bugs in the code.
- `ci-cd-integration`: the scans in the pipeline.
- `test-strategy`: the place of security testing in the overall plan.
