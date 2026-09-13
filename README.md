# AEGIS Analyst

**Role:** P&L / MRR Analyst for Hamid's personal AEGIS agent company (built on Trinity)

AEGIS Analyst is the fourth hire and first Finance specialist in Hamid's personal agent company. It reads AEGIS's real, live revenue data from corp-orchestrator's read-only API and reports it plainly — no spin, no rounding, no forecasting — flagging only obvious arithmetic anomalies to `aegis-ceo`.

## Capabilities

- **Check revenue** — query the live MRR/signup endpoints and report the real figures (`/check-revenue`)
- **Escalate anomaly** — hand a detected arithmetic contradiction to `aegis-ceo` without interpreting it (`/escalate-anomaly`)
- **Trial report** — one-time initial validation run before any recurring cadence starts (`/trial-report`)

## Getting Started

```
cd aegis-analyst && claude
/onboarding
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for how the agent is built today and **[TARGET-ARCHITECTURE.md](TARGET-ARCHITECTURE.md)** for where it's headed.

## Skills

| Skill | Purpose |
|-------|---------|
| `/check-revenue` | Query live MRR/signup data and report it plainly, flagging obvious anomalies |
| `/escalate-anomaly` | Hand off a detected anomaly to aegis-ceo |
| `/trial-report` | One-time initial validation run before recurring reporting starts |
| `/reconcile-docs` | Keep docs, skills, and architecture consistent |
