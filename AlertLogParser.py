#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import re
import json
from datetime import datetime, timedelta

# ========================= CONFIG =========================
LOG_DIR = os.path.expanduser(
    "~/Library/Application Support/net.metaquotes.wine.metatrader4/drive_c/Program Files (x86)/MetaTrader 4/MQL4/Logs"
)
SIGNAL_FILE = os.path.expanduser(
    "~/Library/Application Support/net.metaquotes.wine.metatrader4/drive_c/Program Files (x86)/MetaTrader 4/MQL4/Files/signal.txt"
)
STALE_SECONDS = 15 * 60  # 15 minutes
RISK = 0.5
BROKER_OFFSET_HOURS = 0
STATE_FILE = os.path.expanduser("~/.mt4_alert_state.json")  # persistent dedupe

# ========================= STATE =========================
last_ts_per_symbol = {}
signal_queue = {}

# Load persistent state
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            last_ts_per_symbol = json.load(f)
            last_ts_per_symbol = {k: int(v) for k, v in last_ts_per_symbol.items()}
    except Exception as e:
        print("[WARN] Failed to load state:", e)

# ========================= REGEX =========================
CLASSIC_ALERT_RE = re.compile(
    r"Alert: (\w+) [A-Z0-9]+ Entry point [0-9.]+ \((BUY|SELL)\)"
)
ALL_TF_ALERT_RE = re.compile(
    r"Alert: (\w+) All timeframes are (BUY|SELL)"
)

# ========================= CUSTOM SYMBOL-TIMEFRAMES =========================
ALLOWED_TF = {
    "AUDUSD": ["M5"],
    "AVAUSD": ["M15", "M30"],
    "ETHUSD": ["M5", "M15"],
    "ETHEUR": ["H1"],
    "XRPUSD": ["H1", "H4"],
    "GOLD":   ["M5", "M30"],
    "US100":  ["H1"]
}

# ========================= HELPERS =========================
def atomic_write(path, lines):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    os.replace(tmp_path, path)
    print(f"[WRITE] {len(lines)} signal(s) written to {path}")


def save_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(last_ts_per_symbol, f)
    except Exception as e:
        print("[WARN] Failed to save state:", e)


def parse_broker_time(line):
    match = re.match(r"\d+\t(\d+):(\d+):(\d+).(\d+)", line)
    if not match:
        return int(time.time())
    hh, mm, ss, ms = map(int, match.groups())
    now = datetime.utcnow() + timedelta(hours=BROKER_OFFSET_HOURS)
    broker_dt = now.replace(hour=hh, minute=mm, second=ss, microsecond=ms*1000)
    return int(broker_dt.timestamp())


def process_alert(symbol, direction, rr=1.0, tf=None):
    ts = int(time.time())
    last_ts = last_ts_per_symbol.get(symbol, 0)
    if ts - last_ts < 1:
        print(f"[SKIP] Duplicate/stale alert for {symbol} ({direction})")
        return

    # Filter by allowed timeframes
    if tf and symbol in ALLOWED_TF and tf not in ALLOWED_TF[symbol]:
        print(f"[SKIP] TF {tf} not allowed for {symbol}")
        return

    last_ts_per_symbol[symbol] = ts
    save_state()

    comment = f"MT4_ALERT|RR:{rr}"
    if tf:
        comment += f"|TF:{tf}"

    line = f"{symbol},{direction},{RISK},{comment},{ts}"
    signal_queue[ts] = line
    print(f"[QUEUE] Signal queued: {line}")


def remove_executed_signals():
    """
    Remove executed signals from the top of signal.txt
    """
    if not os.path.exists(SIGNAL_FILE):
        return

    try:
        with open(SIGNAL_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        pending = []
        now = int(time.time())
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 5:
                continue
            ts = int(parts[4])
            # Remove if older than 1 sec (already processed)
            if now - ts > 1:
                continue
            pending.append(line)

        atomic_write(SIGNAL_FILE, pending)
    except Exception as e:
        print("[ERROR] Failed to clean signal.txt:", e)


# ========================= MAIN LOOP =========================
def main():
    print("Starting MT4 Alert Log Parser...")

    files = [f for f in os.listdir(LOG_DIR) if f.lower().endswith(".log")]
    if not files:
        print("[ERROR] No log files found in", LOG_DIR)
        return
    files.sort()
    latest_log = os.path.join(LOG_DIR, files[-1])
    print("[INFO] Using log:", latest_log)

    last_size = 0
    while True:
        try:
            if not os.path.exists(latest_log):
                time.sleep(1)
                continue

            size = os.path.getsize(latest_log)
            if size < last_size:
                last_size = 0
            if size == last_size:
                time.sleep(0.5)
                continue

            with open(latest_log, "r", encoding="utf-8") as f:
                f.seek(last_size)
                lines = f.readlines()
                last_size = f.tell()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                ts = parse_broker_time(line)

                # Classic alert
                m = CLASSIC_ALERT_RE.search(line)
                if m:
                    sym, dir = m.groups()
                    process_alert(sym, dir, rr=1.0)
                    continue

                # All timeframes alert
                m2 = ALL_TF_ALERT_RE.search(line)
                if m2:
                    sym, dir = m2.groups()
                    tf_match = re.search(r" (\w+),([DHmM]\d+): Alert", line)
                    tf = tf_match.group(2) if tf_match else None
                    process_alert(sym, dir, rr=3.0, tf=tf)
                    continue

            # FIFO: sort by timestamp and flush
            if signal_queue:
                ordered_lines = [signal_queue[k] for k in sorted(signal_queue.keys())]
                atomic_write(SIGNAL_FILE, ordered_lines)
                signal_queue.clear()

            # Auto-remove executed signals
            remove_executed_signals()

            time.sleep(0.2)

        except KeyboardInterrupt:
            print("Exiting parser.")
            break
        except Exception as e:
            print("[ERROR]", e)
            time.sleep(1)


if __name__ == "__main__":
    main()
