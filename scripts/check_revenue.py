#!/usr/bin/env python3
"""Read MRR and signups. The model only posts this script's stdout.

GET only. CORP_READONLY_TOKEN only. No other host, no other route.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

SUMMARY_URL = "https://defenseaegis.org/api/corp/v1/bev/summary"
TRAJECTORY_URL = "https://defenseaegis.org/api/corp/v1/bev/trajectory"
UA = "Mozilla/5.0 (compatible; aegis-analyst/1.0; +https://defenseaegis.org)"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _get(url: str, token: str) -> tuple[int, dict]:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "User-Agent": UA},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"error": raw[:200]}
        return exc.code, payload


def mrr_fields(summary: dict) -> tuple[str, str]:
    snap = summary.get("mrr_snapshot") if isinstance(summary, dict) else None
    if not isinstance(snap, dict) or snap.get("unavailable") is True:
        return "not returned by the API", "not returned by the API"
    display = snap.get("mrr_display")
    if display is None and isinstance(snap.get("mrr_cents"), (int, float)):
        currency = snap.get("currency") or ""
        display = f"{snap['mrr_cents'] / 100:.2f} {currency}".strip()
    paying = snap.get("paying_subscribers")
    return (
        str(display) if display is not None else "not returned by the API",
        str(paying) if paying is not None else "not returned by the API",
    )


def latest_signups(trajectory: dict) -> str:
    hist = trajectory.get("signup_history_14d") if isinstance(trajectory, dict) else None
    if not isinstance(hist, list) or not hist or not isinstance(hist[-1], dict):
        return "not returned by the API"
    last = hist[-1]
    if "signups" not in last:
        return "not returned by the API"
    day = last.get("date") or last.get("day") or ""
    return f"{last['signups']}" + (f" on {day}" if day else "")


def delta(current: str, previous: str | None) -> str:
    if previous is None or previous == "":
        return "no prior baseline"
    if current == previous:
        return "unchanged"
    return f"was {previous}"


def render(summary: dict, trajectory: dict, baseline: dict | None) -> str:
    mrr, paying = mrr_fields(summary)
    signups = latest_signups(trajectory)
    base = baseline or {}
    lines = [
        "Task: /check-revenue",
        "What I did: GET /api/corp/v1/bev/summary and /api/corp/v1/bev/trajectory",
        f"MRR: {mrr} ({delta(mrr, base.get('mrr'))})",
        f"Paying subscribers: {paying} ({delta(paying, base.get('paying_subscribers'))})",
        f"Signups: {signups} ({delta(signups, base.get('signups'))})",
        "Outcome: success",
    ]
    return "\n".join(lines)


def snapshot(summary: dict, trajectory: dict) -> dict:
    mrr, paying = mrr_fields(summary)
    return {"mrr": mrr, "paying_subscribers": paying, "signups": latest_signups(trajectory)}


def main() -> int:
    if Path("/home/developer").is_dir():
        os.chdir("/home/developer")
    for candidate in (Path("/home/developer/.env"), Path(".env")):
        load_dotenv(candidate)
    token = os.environ.get("CORP_READONLY_TOKEN", "")
    if not token:
        print("Task: /check-revenue")
        print("Outcome: failure")
        print("CORP_READONLY_TOKEN is missing. No other credential was used.")
        return 1
    summary_status, summary = _get(SUMMARY_URL, token)
    traj_status, trajectory = _get(TRAJECTORY_URL, token)
    if summary_status == 403 or traj_status == 403:
        print("Task: /check-revenue")
        print("Outcome: failure")
        print("HTTP 403 from defenseaegis.org. This is the Cloudflare check, not a rotated token.")
        return 1
    if summary_status == 401 or traj_status == 401:
        print("Task: /check-revenue")
        print("Outcome: failure")
        print("HTTP 401. CORP_READONLY_TOKEN was rejected.")
        return 1
    if summary_status != 200 or traj_status != 200:
        print("Task: /check-revenue")
        print("Outcome: failure")
        print(f"HTTP summary={summary_status} trajectory={traj_status}")
        return 1
    baseline_path = Path("memory/revenue-baseline.json")
    baseline = None
    if baseline_path.is_file():
        baseline = json.loads(baseline_path.read_text())
    print(render(summary, trajectory, baseline))
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(snapshot(summary, trajectory), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
