# Installation

## MetaTrader 4 EA

1. Open MT4.
2. Go to `File → Open Data Folder`.
3. Navigate to `MQL4/Experts/`.
4. Copy `SignalExecutorEA.mq4` there.
5. Open MetaEditor and compile.
6. Attach EA to any chart (doesn't matter which).

---

## Python Parser

1. Ensure Python 3.8+ is installed.
2. Install dependencies if needed (standard library only).
3. Verify the paths at top of `AlertLogParser.py`.
4. Run: python3 AlertLogParser.py

python3 AlertLogParser.py

5. Parser writes to:MQL4/Files/signal.txt
