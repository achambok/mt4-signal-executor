# Usage Guide

### Parser

- Reads the latest MT4 log file.
- Detects alert formats:
  - Classic alerts: `Entry point (BUY/SELL)`
  - All TF alerts: `All timeframes are BUY/SELL`
- Filters by symbol/timeframe.
- Deduplicates signals persistently using `~/.mt4_alert_state.json`.
- Writes atomic FIFO queue to `signal.txt`.

---

### EA

- Monitors `signal.txt` every tick.
- Reads only the first line.
- Validates
  - Market open
  - Spread
  - Timeframes
  - Risk constraints
- Opens trade with calculated SL and RR TP.
- Removes executed signals.
- Moves stop to breakeven at 1R.

---

## Signal Format

SYMBOL,DIRECTION,RISK,COMMENT_WITH_RR_AND_TF,TIMESTAMP

Example:
ETHUSD,BUY,0.5,MT4_ALERT|RR:3.0|TF:M5,1767489001


