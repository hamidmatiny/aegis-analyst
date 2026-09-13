---
name: check-revenue
description: Query corp-orchestrator's read-only API for real MRR and signup figures and report them plainly, flagging any obvious arithmetic anomaly
allowed-tools: Bash, Read, WebFetch
user-invocable: true
metadata:
  version: "1.0"
  created: 2026-09-13
  author: aegis-analyst
---

# Check Revenue

## Purpose

Read AEGIS's real, live revenue numbers from corp-orchestrator's read-only API and report them exactly as returned — no rounding, no estimating, no narrative — then flag only explicit arithmetic anomalies.

## Process

### Step 1: Confirm the credential

Check that `CORP_READONLY_TOKEN` is set (from `.env` locally, or the injected environment on Trinity). If it is missing:
- Do not substitute any other token (never `AEGIS_INTERNAL_TOKEN` or an admin/write credential).
- Ask Hamid directly for `CORP_READONLY_TOKEN` and stop.

### Step 2: Query the endpoints

Make `GET` requests only, with `Authorization: Bearer $CORP_READONLY_TOKEN`, to:
- `https://defenseaegis.org/api/corp/v1/bev/trajectory`
- `https://defenseaegis.org/api/corp/v1/bev/summary`

Never call any other method (no POST/PUT/DELETE) and never call any other route on that host.

MRR lives on `/bev/summary`'s `mrr_snapshot` object: `mrr_display` (or `mrr_usd`/`mrr_cents` + `currency`) and `paying_subscribers`. If `mrr_snapshot.unavailable` is `true` or missing entirely, report "not returned by the API" — do not fall back to a remembered figure.

Signup counts live on `/bev/trajectory`'s `signup_history_14d` array — use the most recent day's entry.

To save tokens, extract only the specific fields you need (MRR, signup count, timestamp, any other headline numeric figures) rather than dumping the full raw payload into context.

### Step 3: Compare against the last known reading

If `mcp__trinity__list_reports` is available, fetch the most recent `aegis_analyst.revenue_snapshot` report to get the last-reported MRR/signup figures for comparison, instead of re-querying historical data. If it's not available (local run), compare against whatever you have in this conversation or skip the comparison.

### Step 4: Report the real number

State plainly:
- Current MRR (exact figure, with currency as returned)
- Current signup count
- Any other numeric field the endpoints returned
- Whether each figure is unchanged, up, or down from the last known reading, and by how much
- For any field the API did not return, say exactly "not returned by the API" — never fill the gap with a guess

Do not interpret what the numbers mean for the business. State the numbers and the delta, nothing more.

### Step 5: Check for obvious anomalies

Flag only explicit, obvious arithmetic problems:
- The two endpoints contradict each other (e.g. summary and trajectory disagree on the same figure for the same period)
- A sudden implausible jump or drop between this reading and the last one

If found, do not explain or interpret the anomaly — hand it to `/escalate-anomaly` with the two conflicting/surprising figures.

### Step 6: Publish the report (Trinity only)

If `mcp__trinity__report` is available, call it:
- `report_type`: `aegis_analyst.revenue_snapshot`
- `display_hint`: `kpi`
- `title`: e.g. "MRR $29.00 CAD — unchanged"
- `payload`: `{ "tiles": [ {"label": "MRR", "value": "29.00", "unit": "CAD"}, {"label": "Signups", "value": "1"} ], "source": "https://defenseaegis.org/api/corp/v1/bev/summary", "checked_at": "<ISO timestamp>" }`

If the tool is unavailable or refuses for lacking an agent-scoped key, skip this step silently — do not retry.

## Outputs

- A plain-language report of the real current MRR, signups, and any other returned figures, with deltas from the last known reading
- An anomaly escalation via `/escalate-anomaly` if one was found
- A published `aegis_analyst.revenue_snapshot` report on Trinity, when available
