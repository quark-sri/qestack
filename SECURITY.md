# Security policy

## Report a vulnerability

Do not open a public issue for a security problem.

Use GitHub private vulnerability reporting: open the **Security** tab of the repository and click **Report a vulnerability**. Give:

- the qestack version,
- the steps to reproduce,
- the effect (for example: the guard hook can be bypassed, a command runs an unexpected program).

The maintainer replies within 7 days.

## Scope notes

- The `qestack hook` command runs with your user permissions inside Claude Code. It reads tool input and the repository. It does not use the network.
- The engine runs the build commands that you configure in `.qestack/project.toml`. Review that file like any build script.
- The guard hook is a convenience. It is not a security boundary. The CI guard is the authority. A hook bypass is a bug, but not a vulnerability, unless it lets an agent run commands that you did not allow.
