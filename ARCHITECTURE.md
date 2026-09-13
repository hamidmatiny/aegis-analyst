# AEGIS Analyst Architecture (Current State)

**What this is:** the agent as it actually runs today. For where it's deliberately headed, see the companion **`TARGET-ARCHITECTURE.md`**. When a target ships, it moves *out* of that doc and *into* this one.

**Last updated:** 2026-09-13

## Overview

AEGIS Analyst is a single-agent Trinity deployment: it holds one read-only credential (`CORP_READONLY_TOKEN`), calls two GET endpoints on `defenseaegis.org`, and reports what it reads — either interactively or via three skills.

## Components

### Skills
- `/check-revenue` — queries the two corp-orchestrator endpoints, reports real figures, flags arithmetic anomalies
- `/escalate-anomaly` — hands an anomaly off to `aegis-ceo`
- `/trial-report` — one-time initial validation run
- `/onboarding` — setup progress tracker
- `/update-dashboard` — refreshes `dashboard.yaml` with the latest reading
- `/reconcile-docs` — checks doc/skill/architecture coherence

### Subagents
None yet.

### Data & State
- `onboarding.json` — local setup progress
- `dashboard.yaml` — live snapshot of the most recent MRR/signup reading
- No local database; all revenue data is read live from corp-orchestrator's API each time, not cached beyond the latest Trinity report

### Schedules
Declared in `template.yaml`, all `enabled: false` until Hamid approves the trial report:
- Daily revenue check (`/check-revenue`, `0 13 * * *`)
- Dashboard refresh (`/update-dashboard`, `0 */6 * * *`)
- Weekly doc reconciliation (`/reconcile-docs`, `0 9 * * 1`)

## Trinity Integration

Runs on the free-pool tier via OmniRoute (`gemini/gemini-3.7-flash`), per `aegis-infra`'s assignment — not the Claude Pro subscription tier. Resources: 1 CPU / 2g memory. Publishes `aegis_analyst.revenue_snapshot`, `aegis_analyst.anomaly`, and `aegis_analyst.kpi_snapshot` reports via `mcp__trinity__report` when deployed.
