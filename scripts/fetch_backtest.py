#!/usr/bin/env python3
"""Pull one backtest from QuantConnect and freeze it as a data file for the site.

Usage:
    export QC_USER_ID=...      # from https://www.quantconnect.com/settings/
    export QC_API_TOKEN=...
    python scripts/fetch_backtest.py --project 12345678 --backtest abc123... --slug my-strategy

Writes data/strategies/<slug>.json. Commit that file; the strategy page reads it.
Never commit your credentials. Keep them in environment variables.

Requires: pip install requests
"""
import argparse, base64, datetime, hashlib, json, os, pathlib, sys, time

import requests

BASE_URL = "https://www.quantconnect.com/api/v2"

# Statistics shown on the strategy page, in display order. Edit freely; names
# must match keys in the "statistics" object QuantConnect returns.
STAT_KEYS = ["Compounding Annual Return", "Sharpe Ratio", "Drawdown", "Total Orders"]


def headers():
    user_id, token = os.environ["QC_USER_ID"], os.environ["QC_API_TOKEN"]
    timestamp = str(int(time.time()))
    hashed = hashlib.sha256(f"{token}:{timestamp}".encode()).hexdigest()
    auth = base64.b64encode(f"{user_id}:{hashed}".encode()).decode("ascii")
    return {"Authorization": f"Basic {auth}", "Timestamp": timestamp}


def post(endpoint, payload):
    r = requests.post(f"{BASE_URL}/{endpoint}", headers=headers(), json=payload, timeout=60)
    r.raise_for_status()
    body = r.json()
    if not body.get("success"):
        sys.exit(f"{endpoint} failed: {body.get('errors')}")
    return body


def fetch_equity(project_id, backtest_id, start, end):
    """Read the 'Strategy Equity' chart. The chart may still be generating on
    the first call, so retry a few times."""
    payload = {"projectId": project_id, "backtestId": backtest_id, "name": "Strategy Equity",
               "count": 500, "start": start, "end": end}
    for _ in range(10):
        body = post("backtests/chart/read", payload)
        chart = body.get("chart")
        if chart:
            break
        time.sleep(3)
    else:
        sys.exit("Equity chart was not ready; try again in a minute.")
    points = chart["series"]["Equity"]["values"]
    equity = []
    for p in points:
        # Points arrive either as [time, open, high, low, close] or {"x":..., "y":...}
        t, v = (p[0], p[-1]) if isinstance(p, list) else (p["x"], p["y"])
        date = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).date().isoformat()
        equity.append({"date": date, "value": round(float(v), 2)})
    return equity


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=int, required=True)
    ap.add_argument("--backtest", required=True)
    ap.add_argument("--slug", required=True, help="file name, e.g. quality-momentum")
    args = ap.parse_args()

    bt = post("backtests/read", {"projectId": args.project, "backtestId": args.backtest})["backtest"]
    stats = bt.get("statistics", {})
    to_unix = lambda s: int(datetime.datetime.fromisoformat(s.replace("Z", "+00:00").replace(" ", "T"))
                            .replace(tzinfo=datetime.timezone.utc).timestamp())
    start, end = bt["backtestStart"], bt["backtestEnd"]
    equity = fetch_equity(args.project, args.backtest, to_unix(start), to_unix(end))

    out = {
        "meta": {"strategy": args.slug, "placeholder": False, "project_id": args.project,
                 "backtest_id": args.backtest, "start": start[:10], "end": end[:10],
                 "retrieved": datetime.date.today().isoformat()},
        "statistics": {k: stats[k] for k in STAT_KEYS if k in stats},
        "equity": equity,
    }
    path = pathlib.Path(__file__).resolve().parent.parent / "data" / "strategies" / f"{args.slug}.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"Wrote {path} ({len(equity)} equity points)")


if __name__ == "__main__":
    main()
