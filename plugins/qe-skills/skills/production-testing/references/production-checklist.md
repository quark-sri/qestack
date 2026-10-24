# Production testing checklist

## Post-deploy smoke check

- Runs after each deploy, in under a few minutes, and blocks or reverses the rollout when it fails.
- Checks the version that runs, the health endpoint, one read path and one safe write path.
- Uses a test account. Marks its data so that reports and billing ignore it.

## Synthetic journeys

- One check for each critical journey, run on a schedule from outside the network.
- Fails only on a real defect. Retry once for a network error, and report the retry.
- Keeps the run history, so that the team can see the trend.

## Signals that act as tests

| Signal | Question |
|---|---|
| Error rate | Does the rate of server errors stay under the agreed limit? |
| Latency | Do the slow percentiles stay under the agreed limit? |
| Saturation | Do the queues, pools and disks have room? |
| Business numbers | Do orders, logins and payments stay in the normal range for this hour? |
| Logs and traces | Can a person follow one request through all services with one ID? |

## Staged rollout

| Step | Share of traffic | Observe | Stop or reverse when |
|---|---|---|---|
| 1 | Small group, or internal users | Write the time | Write the exact numbers |
| 2 | Larger group | Write the time | Write the exact numbers |
| 3 | Everyone | Write the time | Write the exact numbers |

Write the numbers before the rollout. Decide who has the right to stop it.

## Alert quality

- Has an owner, a runbook link and a clear action.
- Fires for a real problem. It has a test that proves it.
- Does not fire all the time. Review the alerts that fired and needed no action.

## Data rules

- No real customer data in tests. No real payments.
- Every created record is marked, and is removed or ignored by the reports.
- Never allowed: bulk writes, load against production without an agreement, tests that change real accounts.

## Drills

- Roll back to the last version, and check the data and the clients.
- Switch a flag off, and check that the old path works.
- Restore from backup in a safe place, and measure the time.
