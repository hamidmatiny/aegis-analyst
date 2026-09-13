---
name: onboarding
description: Track your setup progress — shows what's done, what's next, and walks you through each step
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
user-invocable: true
metadata:
  version: "1.0"
  created: 2026-09-13
  author: aegis-analyst
---

# Onboarding

Track and continue your setup progress. This skill reads `onboarding.json`, shows your current status, and walks you through the next incomplete step.

## Process

### Step 1: Load State

Read `onboarding.json` from the agent root directory. If it doesn't exist, inform the user that onboarding is complete or the file was removed.

### Step 2: Show Progress

Display a checklist grouped by phase. Mark the current phase with an arrow.

```
## AEGIS Analyst — Setup Progress

### Phase 1: Local Setup  ← current
- [ ] Set CORP_READONLY_TOKEN in .env
- [ ] Run /trial-report and confirm real figures
- [ ] Install plugins (agent-dev, trinity)

### Phase 2: Trinity Deployment
- [ ] Deploy to Trinity
- [ ] Run /check-revenue remotely

### Phase 3: Schedules
- [ ] Enable daily /check-revenue schedule (after trial approved)
- [ ] Verify first scheduled execution

**Progress: 0/7 complete**
```

### Step 3: Guide Next Step

Identify the first incomplete step in the current phase and guide it:

**For `env_configured`:**
- Check if `.env` exists (`cp .env.example .env` if not).
- The only required variable is `CORP_READONLY_TOKEN` — the read-only, GET-only token `aegis-ceo` also uses. Tell the user to ask Hamid for it directly if it isn't already available. Never accept `AEGIS_INTERNAL_TOKEN` or any admin/write token as a substitute.
- After confirmed set, mark done.

**For `trial_report_run`:**
- Tell the user to run `/trial-report`.
- After it completes with real (non-placeholder) figures, mark done.

**For `plugins_installed`:**
- Run:
  ```
  /plugin install agent-dev@abilityai
  /plugin install trinity@abilityai
  ```
- Note successes and failures. After attempted, mark done.

**For `onboarded` (Trinity phase):**
- Guide the user to run `/trinity:onboard`.
- After completion, mark done and advance phase.

**For `first_remote_run`:**
- Tell user to run `/check-revenue` remotely via `mcp__trinity__chat_with_agent`.
- After completion, mark done and advance phase.

**For `schedules_configured`:**
- Only proceed if the trial report has already been approved by Hamid.
- Guide flipping the "Daily revenue check" schedule in `template.yaml` from `enabled: false` to `enabled: true`, then re-running `/trinity:onboard` (or `/trinity:sync`) to reconcile it onto the live agent.
- After completion, mark done.

**For `first_scheduled_run`:**
- Tell user to check `mcp__trinity__get_schedule_executions` for execution confirmation.
- After verified, mark done.

### Step 4: Update State

After each step is completed, update `onboarding.json`:
- Set the step's `done` to `true`
- If all steps in current phase are done, advance `phase` to the next phase
- If all phases complete, congratulate the user

### Step 5: Phase Transitions

**Local → Trinity:**
```
## Local Setup Complete!

AEGIS Analyst is configured and has produced a real trial report locally.

Ready to go live alongside aegis-ceo and aegis-infra? Run /onboarding again
when you're ready to set up Trinity.
```

**Trinity → Schedules:**
```
## Trinity Deployment Complete!

AEGIS Analyst is live on Trinity. Once Hamid has reviewed the trial report,
run /onboarding to enable the daily revenue-check schedule.
```

**All Complete:**
```
## Onboarding Complete!

AEGIS Analyst is fully set up:
- Local environment configured
- Deployed to Trinity
- Daily revenue-check schedule running

onboarding.json can be kept as a record or deleted.
```

## Outputs

- Updated `onboarding.json` with progress
- Step-by-step guidance for the current task
- Phase transition messages at milestones
