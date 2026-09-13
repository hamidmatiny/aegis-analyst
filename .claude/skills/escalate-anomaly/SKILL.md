---
name: escalate-anomaly
description: Package a detected arithmetic anomaly in AEGIS's revenue data and hand it off to aegis-ceo without interpreting its business meaning
allowed-tools: Read, Write, Bash, mcp__trinity__chat_with_agent, mcp__trinity__report, mcp__trinity__list_agents
user-invocable: true
metadata:
  version: "1.1"
  created: 2026-09-13
  author: aegis-analyst
---

# Escalate Anomaly

## Purpose

Hand a detected arithmetic anomaly (contradiction between endpoints, or an implausible jump/drop) to `aegis-ceo`, stating only the facts of the discrepancy — never its likely business cause or meaning.

**Fail-closed delivery:** claim **"escalated to aegis-ceo"** only after `mcp__trinity__chat_with_agent` returns a confirmed successful delivery. On any failure, say **"flagged, delivery failed"** (and what failed) — never silently imply the CEO was notified.

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

### Step 3: Deliver to aegis-ceo (required attempt)

1. Call `mcp__trinity__chat_with_agent` with `name: "aegis-ceo"` and a message that includes the anomaly note, e.g.:
   ```
   /handle-anomaly source=aegis-analyst
   <anomaly note>
   ```
   (If `aegis-ceo` has no such playbook, the message still counts as delivery when the chat call succeeds — CEO can triage in chat.)
2. **Confirmed delivery** = the tool call succeeds (HTTP/MCP success) and returns an execution/response from `aegis-ceo` (not a permission error, timeout with no ack, or empty refusal).
3. On **confirmed delivery**: you may say the anomaly was **escalated to aegis-ceo**. Proceed to Step 4 with `delivery: confirmed`.
4. On **any failure** (permission denied, tool missing, timeout, error): say exactly **"flagged, delivery failed"** and include the error. Do **not** say escalated, notified, or handed off to the CEO. Proceed to Step 4 with `delivery: failed` and still publish the flag so Hamid has a durable record.
5. Requires live A2A permission `aegis-analyst` → `aegis-ceo`. If denied, that is a delivery failure — same wording.

### Step 4: Publish the flag (Trinity only)

If `mcp__trinity__report` is available, call it:
- `report_type`: `aegis_analyst.anomaly`
- `display_hint`: `markdown`
- `title`: short one-line description of the discrepancy
- `payload`: `{ "markdown": "<the anomaly note>", "delivery": "confirmed"|"failed", "delivery_detail": "<ack or error>" }`

Title/body must not claim CEO notification unless `delivery` is `confirmed`.

Skip the report tool silently if unavailable — but still state delivery outcome in chat.

## Known failure modes

### FM-1 — Claiming escalated without delivery

**What went wrong:** Skill prose used fictional SendMessage/ListAgents; no MCP chat tools; no analyst→ceo permission — yet a Trinity anomaly report could still look like the CEO was notified.

**Correct behavior:** Only `chat_with_agent` success → "escalated". Otherwise "flagged, delivery failed".

## Outputs

- Chat: either **escalated to aegis-ceo** (confirmed) or **flagged, delivery failed** (with error)
- A published `aegis_analyst.anomaly` report on Trinity when available, with explicit `delivery` field
