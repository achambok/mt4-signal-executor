# System Architecture

## Parser

- Watches MT4 `Logs/*.log`.
- Parses broker‑time timestamps.
- Detects alert formats:
  - Classic
  - All TF
- Normalizes alerts.
- Adds only allowed TF signals.
- Writes FIFO queue.
- Persists dedupe state in JSON.

---

## FIFO Queue

Keys:

- Signals sorted by timestamp.
- `signal.txt` always represents the next line to trade.
- After execution, EA removes top line.

---

## EA Execution Logic

1. Read top signal.
2. Validate:
   - Market open
   - Spread
   - Risk
   - Timeframe
3. Compute SL via ATR + Swing.
4. Compute TP via RR.
5. Open trade.
6. Remove signal.

---

## Risk Management

- Max trades per day
- Max open risk %
- Max daily loss %
- Spread filter
- Session filter

Every check is logged.

---

## Breakeven / TP Behavior

- On first 1R, stop is moved to entry.
- Original TP preserved.
- Works for BUY/SELL.

7. EA and Parser Files
	•	Place SignalExecutorEA.mq4 into EA/
	•	Place AlertLogParser.py into parser/

(You already have those — no changes beyond what we built.)


