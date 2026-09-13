# AEGIS Analyst Target Architecture

**What this is:** where the agent is deliberately headed. The companion to **`ARCHITECTURE.md`** (what runs today). When something here ships, it moves *out* of this doc and *into* `ARCHITECTURE.md`.

**Last updated:** 2026-09-13

## Direction

Stay narrow and cheap: this agent should never grow scope beyond reading and reporting real numbers. It should never gain a write credential, never do forecasting or business interpretation, and never move off the free-pool tier without `aegis-infra` explicitly reassigning it. Growth here means *more reliable reporting*, not *more analysis*.

## Planned Capabilities

- **Historical trend memory** — persist a lightweight local log of past revenue snapshots (timestamp, MRR, signups) so `/check-revenue` can compute deltas without depending on `mcp__trinity__list_reports` being available. Depends on: agreeing with `aegis-infra` on where that log lives so it doesn't conflict with the "reuse memory over re-querying" token-saving habit already in place.
- **Direct aegis-ceo handoff protocol** — a firmer, shared playbook-call contract with `aegis-ceo` for `/escalate-anomaly` (structured fields instead of free text) once `aegis-ceo`'s own playbook surface is stable enough to target. Depends on: `aegis-ceo` publishing a stable `/handle-anomaly` signature.
- **Multi-metric expansion** — if corp-orchestrator's read-only API adds more numeric fields beyond MRR/signups (e.g. churn, ARPU), extend `/check-revenue` to report those too, under the same plain-reporting discipline. Depends on: those fields actually existing in the API — do not build ahead of the endpoint.
