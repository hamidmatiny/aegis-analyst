---
name: update-dashboard
description: Refresh dashboard.yaml with the most recent real revenue check
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
metadata:
  version: "1.0"
  created: 2026-09-13
  author: aegis-analyst
---

# Update Dashboard

Refresh `dashboard.yaml` with the latest real MRR/signup figures.

## Process

### Step 1: Gather Metrics

- If `mcp__trinity__list_reports` is available, fetch the most recent `aegis_analyst.revenue_snapshot` and `aegis_analyst.anomaly` reports.
- Otherwise, run `/check-revenue` to get a fresh real reading.

### Step 2: Update Dashboard

Read `dashboard.yaml`, update:
- `updated` timestamp to now
- "Current MRR" and "Signups" metric values to the real figures
- "Anomaly Status" widget: "None" (green) or "Flagged" (red) based on the latest check
- "Recent Checks" list with the last few readings (timestamp + MRR)

Write the updated `dashboard.yaml`.

### Step 3: Publish a KPI snapshot report (Trinity)

If `mcp__trinity__report` is available, publish the same figures:
- `report_type`: `aegis_analyst.kpi_snapshot`
- `display_hint`: `kpi`
- `payload`: `{ "tiles": [ {"label": "MRR", "value": "...", "unit": "..."}, {"label": "Signups", "value": "..."} ] }`

Skip silently if unavailable.

### Step 4: Confirm

Report what was updated:
```
Dashboard refreshed:
- MRR: [old] → [new]
- Signups: [old] → [new]
- Last updated: [timestamp]
```

Note: On Trinity remote, the dashboard path is `/home/developer/dashboard.yaml`.

## Outputs

- Updated `dashboard.yaml` with the latest real revenue figures
