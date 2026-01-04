# mt4-signal-executor

mt4‑signal‑executor/
├── EA/
│   └── SignalExecutorEA.mq4
├── parser/
│   └── AlertLogParser.py
├── README.md
├── LICENSE
└── docs/
    ├── INSTALL.md
    ├── USAGE.md
    └── DESIGN.md


# MT4 Signal Executor & Alert Log Parser

This repository contains a **MetaTrader 4 Expert Advisor** and a companion **Python alert log parser** that together create a robust and safe auto‑trading pipeline from MT4 indicator alerts.

---

## 📦 Contents

- `EA/SignalExecutorEA.mq4` – MetaTrader 4 Expert Advisor
- `parser/AlertLogParser.py` – Python parser for MT4 Journal alerts
- `docs/` – Documentation

---

## 📌 Key Features

✔ Atomic FIFO signal queue  
✔ Persistent deduplication  
✔ Per‑symbol allowed timeframes  
✔ BUY/SELL directional filters  
✔ Spread/Session/Risk protection  
✔ ATR + swing stop loss  
✔ Risk reward TP logic  
✔ Breakeven logic and RR ladders  
✔ Auto‑remove executed signals  
✔ Broker timezone alignment

---

## 🚀 Quick Start

### 1. Place the EA in MT4

Copy `SignalExecutorEA.mq4` to:

/MQL4/Experts/
Compile in MetaEditor and add to a chart.

---

### 2. Run the Parser

Make sure Python 3 is installed. Then run: python3 parser/AlertLogParser.py

This monitors the MT4 logs and writes to `signal.txt`.

---

## 📄 More Details

🔗 See `docs/INSTALL.md`  
🔗 See `docs/USAGE.md`  
🔗 See `docs/DESIGN.md`


