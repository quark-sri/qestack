# Exploration heuristics

## Test tours

| Tour | Idea |
|---|---|
| Money | Follow the flows that earn or move money |
| Landmark | Go from one key feature to the next in different orders |
| Back alley | Use the features that few users use |
| All-nighter | Leave the application open for a long time, let sessions expire |
| Saboteur | Remove resources: network, disk, permissions, a dependency |
| Antisocial | Do the opposite of the expected input or order |
| Garbage collector | Visit each screen or endpoint once, quickly |

## Interruptions

- Back, refresh, double submit, two browser tabs, close and reopen.
- Lose the network in the middle of an action. Slow network.
- Session expiry during a long form.

## CRUD and life cycle

- Create, read, update, delete each object. Use it after delete.
- Each status transition, also the forbidden ones.

## Data

- Limits, empty, very long, special characters, other languages, copy and paste.
- Data from another user or tenant.

## Users and roles

- Each role. A role change during a session. A disabled user.

## Consistency

- The same data on different screens, exports, emails and reports.
- Undo, cancel and history.

## Configuration

- Another locale, time zone, screen size, browser zoom, dark mode, keyboard only.
