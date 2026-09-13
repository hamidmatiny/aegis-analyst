---
name: escalate-anomaly
description: Package a detected arithmetic anomaly in AEGIS's revenue data and hand it off to aegis-ceo without interpreting its business meaning
allowed-tools: Read, Write
user-invocable: true
metadata:
  version: "1.0"
  created: 2026-09-13
  author: aegis-analyst
---

# Escalate Anomaly

## Purpose

Hand a detected arithmetic anomaly (contradiction between endpoints, or an implausible jump/drop) to `aegis-ceo`, stating only the facts of the discrepancy — never its likely business cause or meaning.

## Process

### Step 1: Confirm this is an arithmetic anomaly, not a judgment call

Valid triggers:
- Two calls to the corp-orchestrator API (same or different endpoints) return contradictory figures for what should be the same number
- A figure jumps or drops by an implausible amount between consecutive checks

Not valid triggers: MRR being low, growth being slow, or any other figure that is simply unfavorable but internally consistent. Those are not anomalies — they're just the real number. Do not escalate those; report them plainly via `/check-revenue` instead.

### Step 2: State the discrepancy plainly

Write a short, factual anomaly note:
- The two conflicting figures (with their exact values, sources/endpoints, and timestamps)
- Nothing about why it might have happened or what it means for the business — that's for `aegis-ceo` or Hamid to judge

### Step 3: Hand off to aegis-ceo

If `aegis-ceo` is reachable as another agent in this session (check with ListAgents), send the anomaly note directly via SendMessage, addressed as a playbook-style call, e.g.:
```
/handle-anomaly source=aegis-analyst
<anomaly note>
```

If `aegis-ceo` is not reachable in this session, tell Hamid the anomaly note directly so he can relay it, and note that the escalation could not be delivered agent-to-agent this run.

### Step 4: Publish the report (Trinity only)

If `mcp__trinity__report` is available, call it:
- `report_type`: `aegis_analyst.anomaly`
- `display_hint`: `markdown`
- `title`: short one-line description of the discrepancy
- `payload`: `{ "markdown": "<the anomaly note>" }`

Skip silently if the tool is unavailable.

## Outputs

- An anomaly note handed off to `aegis-ceo` (or surfaced to Hamid if aegis-ceo is unreachable)
- A published `aegis_analyst.anomaly` report on Trinity, when available
