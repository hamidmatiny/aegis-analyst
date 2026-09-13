---
name: trial-report
description: One-time initial validation run — confirm the read-only token and API are reachable, then produce one real trial revenue report before any recurring cadence starts
allowed-tools: Bash, Read, WebFetch, AskUserQuestion
user-invocable: true
metadata:
  version: "1.0"
  created: 2026-09-13
  author: aegis-analyst
---

# Trial Report

## Purpose

Deliberately narrow first run: prove the credential and API work, and hand Hamid one real (not placeholder) trial report before turning on any scheduled reporting cadence.

## Process

### Step 1: Confirm the credential is present

Check `CORP_READONLY_TOKEN` is set. If missing, ask Hamid for it directly (never substitute `AEGIS_INTERNAL_TOKEN` or any other credential) and stop until it's provided.

### Step 2: Confirm reachability

Make a single `GET` request to `https://defenseaegis.org/api/corp/v1/bev/summary` with `Authorization: Bearer $CORP_READONLY_TOKEN`. Confirm you get a real response, not an error. If it fails, report the exact error to Hamid (status code, message) — do not fabricate a figure to fill in for a failed call.

### Step 3: Run one real check

Run the same query steps as `/check-revenue` once, end to end, against both endpoints, and produce the report with real figures — not a placeholder or example number.

### Step 4: Present the trial result to Hamid

Show the real MRR, signups, and any other returned figures, plus confirm:
- Token: confirmed working
- API: reachable
- Anomaly check: none found / found (if found, route through `/escalate-anomaly`)

### Step 5: Ask before scheduling

Use AskUserQuestion to confirm with Hamid whether to proceed to enabling the `/check-revenue` schedule in `template.yaml` (currently `enabled: false` by design) now that a real example has been seen.

## Outputs

- Confirmation that the credential and API are working
- One real trial revenue report (not a placeholder)
- A decision from Hamid on whether to enable the recurring `/check-revenue` schedule
