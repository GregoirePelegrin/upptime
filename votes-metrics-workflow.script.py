"""Fetch voting-similarities metrics and send a Telegram summary (+ alert when threshold exceeded)."""
import os
import sys

import requests

METRICS_URL = os.environ["VOTES_METRICS_URL"]
API_KEY = os.environ["VOTES_METRICS_API_KEY"]
BOT_KEY = os.environ["TELEGRAM_BOT_KEY"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
THRESHOLD = int(os.environ.get("METRICS_ALERT_THRESHOLD", "100"))


def main() -> int:
    resp = requests.get(
        METRICS_URL,
        params={"days": 7},
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10,
    )
    resp.raise_for_status()
    m = resp.json()

    top = sorted(m["per_endpoint"].items(), key=lambda x: -x[1])[:3]
    lines = [
        "Votes Similarities — metriques sur 7 jours",
        f"Total: {m['total']}  |  Aujourd'hui: {m['today']}",
        f"Moyenne/jour: {m['avg_per_day']:.1f}",
        "",
        "Top endpoints:",
    ]
    for ep, cnt in top:
        lines.append(f"  - {ep}: {cnt}")

    if m["today"] > THRESHOLD:
        lines.append("")
        lines.append(f"Alerte: {m['today']} requetes aujourd'hui (seuil: {THRESHOLD})")

    text = "\n".join(lines)
    print(text)

    r = requests.post(
        f"https://api.telegram.org/bot{BOT_KEY}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    )
    r.raise_for_status()
    print("Telegram message sent.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
