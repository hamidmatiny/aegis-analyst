---
name: check-revenue
description: Query corp-orchestrator's read-only API for real MRR and signup figures and report them plainly, flagging any obvious arithmetic anomaly
allowed-tools: Bash, Read, WebFetch, mcp__trinity__chat_with_agent, mcp__trinity__list_reports, mcp__trinity__report
user-invocable: true
metadata:
  version: "1.1"
  created: 2026-09-13
  author: aegis-analyst
---

# Check Revenue

## Purpose

Read AEGIS's real, live revenue numbers from corp-orchestrator's read-only API and report them exactly as returned — no rounding, no estimating, no narrative — then flag only explicit arithmetic anomalies. Before publishing outbound, run an **independent** free-pool verification pass (claim + sources only).

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

To save tokens, extract only the specific fields you need (MRR, signup count, timestamp, any other headline numeric figures) rather than dumping the full raw payload into context. **Keep those excerpts** for Step 5.

### Step 3: Compare against the last known reading

If `mcp__trinity__list_reports` is available, fetch the most recent `aegis_analyst.revenue_snapshot` report to get the last-reported MRR/signup figures for comparison, instead of re-querying historical data. If it's not available (local run), compare against whatever you have in this conversation or skip the comparison.

### Step 4: Draft the claim (do not publish yet)

Assemble the outbound claim text — keep metrics on the endpoints that own them:
- **MRR** from `summary.mrr_snapshot` only (`mrr_display` / currency)
- **Paying subscribers** from `summary.mrr_snapshot.paying_subscribers` only
- **Signups** from `trajectory.signup_history_14d` (most recent day) only — this is **not** a subscriber count
- Whether each figure is unchanged, up, or down from the last known reading of **that same field**, and by how much
- For any field the API did not return, say exactly "not returned by the API" — never fill the gap with a guess

Do **not** invent a trajectory "paying" / "subscriber" figure. `/bev/trajectory` does not return `paying_subscribers`.

Do not interpret what the numbers mean for the business. State the numbers and the delta, nothing more.

### Step 5: Independent verification (required before publish)

Before Slack/Trinity publish, get a **separate** free-pool check that does **not** see this chat's reasoning trail:

1. Call `mcp__trinity__chat_with_agent` targeting **`aegis-infra`** with a message that contains **only**:
   - Instruction: run `/verify-revenue-claim`
   - **Claim:** the draft MRR, currency, subscribers/signups, checked_at
   - **Sources:** the JSON excerpts from Step 2 (summary `mrr_snapshot` + relevant trajectory signup entry)
2. Do **not** include your analysis narrative, anomaly speculation, or prior tool logs beyond those excerpts.
3. Expect a one-line `PASS: …` or `FAIL: …` reply.
4. On `FAIL`: do **not** publish. Fix the claim, re-query if needed, or hand to `/escalate-anomaly`. Re-run this step after a fix.
5. On `PASS`: proceed to Step 6 / 7.
6. If `chat_with_agent` is unavailable (local run without Trinity MCP): state plainly that independent verification was **skipped (no Trinity chat)**. Local drafts may be shown to Hamid as **unverified**. **Never** publish a Trinity revenue report for a skipped verify — skip is not publish-worthy.
7. If the call fails with a **permission denied** (or any error that is not a clear `PASS` line): treat as **not verified** — do **not** publish. Escalate: analyst needs `POST /api/agents/aegis-analyst/permissions/aegis-infra` (or equivalent) before the loop can complete.

### Step 6: Check for obvious anomalies

Flag only explicit, obvious arithmetic problems on **the same metric from a source that actually returns it**:
- A sudden implausible jump or drop vs the last known reading of **that same field** (e.g. `mrr_snapshot.mrr_cents` or `paying_subscribers` vs prior revenue snapshot; or latest `signup_history_14d.signups` vs prior signup reading)
- Internal contradiction **inside** `mrr_snapshot` if present (e.g. `mrr_cents` inconsistent with `paying_subscribers × monthly_unit_cents` when all fields are present and `unavailable` is false)

**Not an anomaly (do not escalate):**
- Comparing `summary.mrr_snapshot.paying_subscribers` to anything on `/bev/trajectory` — trajectory has **no** `paying_subscribers`; it only has `signup_history_14d` / chart `signups` (different concept)
- Comparing today's signups to paying subscribers (signups ≠ subscribers)
- Inferring or defaulting a missing field to `0` and treating that as a contradiction

If a real anomaly is found, do not explain or interpret it — hand it to `/escalate-anomaly` with the two conflicting/surprising figures **and their exact JSON paths**. A corrected figure still publishes via Step 7 **only** after an explicit Step 5 `PASS:` — never after skip, deny, or failure.

### Step 7: Publish the report (Trinity only; after PASS only)

**Publish gate:** Step 5 must have returned an explicit `PASS:` line. Skip, deny, timeout, or any non-PASS result → **do not publish**.

If (and only if) Step 5 returned `PASS:` and `mcp__trinity__report` is available, call it:
- `report_type`: `aegis_analyst.revenue_snapshot`
- `display_hint`: `kpi`
- `title`: e.g. "MRR $29.00 CAD — unchanged"
- `payload`: `{ "tiles": [ {"label": "MRR", "value": "29.00", "unit": "CAD"}, {"label": "Signups", "value": "1"} ], "source": "https://defenseaegis.org/api/corp/v1/bev/summary", "checked_at": "<ISO timestamp>", "verified_by": "aegis-infra:/verify-revenue-claim" }`

If the tool is unavailable or refuses for lacking an agent-scoped key, skip this step silently — do not retry.

## Known failure modes

### FM-1 — CLAUDE.md / skill prose drifting from live API shape

**What went wrong:** Docs claimed MRR fields that the live HTTP response did not return (or returned under a different shape), so reports looked authoritative while the read path was empty/wrong.

**Correct behavior:** Always trust the live `mrr_snapshot` / trajectory payload over remembered figures. If a field is missing, say "not returned by the API."

### FM-3 — Publishing after verify skip / permission denial

**What went wrong:** A run could draft real MRR, fail to reach `aegis-infra` (empty A2A permission), skip verify, and still call `mcp__trinity__report`.

**Correct behavior:** Publish only after an explicit `PASS:` line from `/verify-revenue-claim`. Permission errors and skips are not PASS.

### FM-4 — Treating trajectory signups as paying_subscribers

**What went wrong:** Anomaly / E2E paths compared `mrr_snapshot.paying_subscribers` to a fabricated "trajectory paying count" (sometimes defaulted to 0). Live `/bev/trajectory` has **no** `paying_subscribers` — only `signup_history_14d[].signups`. That is a comparison-logic bug, not a data-integrity issue.

**Correct behavior:** Never invent trajectory subscriber fields. Never escalate signup≠subscriber. Only compare a field to another reading of the **same** field from a source that returns it.

## Outputs

- A plain-language report of the real current MRR, signups, and any other returned figures, with deltas from the last known reading
- An independent `PASS`/`FAIL` from `aegis-infra` `/verify-revenue-claim` when Trinity chat is available
- An anomaly escalation via `/escalate-anomaly` if one was found
- A published `aegis_analyst.revenue_snapshot` report on Trinity only after PASS (when available)
