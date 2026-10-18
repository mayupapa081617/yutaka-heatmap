"""TOP10 new entrant push notifications via ntfy. GitHub Actions persists state."""
import json
import os
import sys
import urllib.request
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo
from pressure_core import top_ten

STATE = Path(".alert_state.json")
WATCHLIST = Path("watchlist.txt")
JST = ZoneInfo("Asia/Tokyo")


def send_ntfy(topic, title, message, click_url=""):
    # Topic must be a long unguessable string. Never print or commit the topic.
    url = "https://ntfy.sh/" + topic
    headers = {"Title": title.encode("utf-8").decode("utf-8"), "Tags": "chart_with_upwards_trend", "Priority": "default"}
    # HTTP headers require latin-1; RFC2047 encode Japanese title.
    from email.header import Header
    headers["Title"] = Header(title, "utf-8").encode()
    if click_url.startswith("https://"):
        headers["Click"] = click_url
    req = urllib.request.Request(url, data=message.encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status >= 300:
            raise RuntimeError(f"ntfy HTTP {res.status}")


def main():
    now = datetime.now(JST)
    if now.weekday() >= 5 or not (time(9, 20) <= now.time() < time(11, 30) or time(12, 50) <= now.time() < time(15, 30)):
        print("Outside monitoring window (JST).")
        return
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic or not topic.replace("-", "").replace("_", "").isalnum():
        raise RuntimeError("Set a long random NTFY_TOPIC GitHub Actions secret.")
    raw = WATCHLIST.read_text(encoding="utf-8")
    ranked = top_ten(raw)
    if ranked.empty:
        print("No eligible completed 5-minute bars; keeping previous state.")
        return
    current = {str(row["コード"]): row for row in ranked.to_dict("records")}
    session = "AM" if now.time() < time(12, 0) else "PM"
    key = f"{now.date()}-{session}"
    previous = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    if previous.get("session") != key:
        # Baseline: avoid sending every existing top-ten name at startup.
        print("First valid scan in session: baseline only, no push.")
        STATE.write_text(json.dumps({"session": key, "codes": list(current), "last_scan": now.isoformat()}, ensure_ascii=False))
        return
    previous_codes = set(previous.get("codes", []))
    newcomers = [row for code, row in current.items() if code not in previous_codes]
    if newcomers:
        lines = [f"{row['銘柄']}（{row['コード']}） 第{i}位 / {row['スコア']}点 / VWAP {row['VWAP乖離%']:+.1f}% / 5分足 {row['足時刻']}" for i, row in enumerate(ranked.to_dict("records"), 1) if str(row["コード"]) not in previous_codes]
        send_ntfy(topic, "買い圧力TOP10 新規ランクイン", "\n".join(lines), os.environ.get("HEATMAP_URL", ""))
        print(f"Sent {len(newcomers)} new entrant(s).")
    else:
        print("No new entrants.")
    # Write state only after successful notification, so failures can be retried.
    STATE.write_text(json.dumps({"session": key, "codes": list(current), "last_scan": now.isoformat()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
