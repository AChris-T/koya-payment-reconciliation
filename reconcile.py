#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime

# Latest attempt per txn_id. Events aren't in time order, so compare timestamps.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # truncated / unreadable line
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue
        ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        prev = latest.get(event["txn_id"])
        if prev is None or ts > prev[0]:
            latest[event["txn_id"]] = (ts, event)

total = 0.0
count = 0
for _, event in latest.values():
    if event["status"] == "success":
        # Some amounts arrive as strings with thousands separators, e.g. "55,707.77".
        total += float(str(event["amount"]).replace(",", ""))
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
