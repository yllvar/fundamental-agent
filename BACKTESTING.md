# Backtesting Signals on Historical Data

## Concept

Leverage the 30-instrument, 7-timeframe parquet dataset (`data/historical/`) to evaluate how our existing forex signals would have performed historically.

No trade simulation — no entries, exits, stops, or position sizing. Just signal → forward-candle outcome statistics. Keeps results honest and the code simple.

## Data Source

All data comes from the already-working `services/historical_data_service.py`, which downloads and caches parquet files from [Yllvar/fx-historical-data](https://huggingface.co/datasets/Yllvar/fx-historical-data) on first request.

| Timeframe | Bars per instrument | Coverage |
|---|---|---|
| M1 | 200,000 | ~6 months |
| M5 | 200,000 | ~2.5 years |
| M15 | 200,000 | ~7 years |
| M30 | 200,000 | ~14 years |
| H1 | ~100,000 | ~14 years |
| H4 | ~25,000 | ~14 years |
| D1 | ~5,000 | ~18 years |

## Signals to Backtest

### 1. RSI Reversal
- **Logic**: RSI(14) crosses below `threshold` (default 30) → look for bounce
- **Outcome**: Price change over next N candles
- **Data needed**: Close prices only

### 2. ATR Breakout
- **Logic**: Current candle range > `multiplier` × ATR(14) → continuation?
- **Outcome**: Next-candle direction and magnitude
- **Data needed**: High, Low, Close

### 3. Moving Average Cross
- **Logic**: SMA(fast) crosses above/below SMA(slow) → trend persistence
- **Outcome**: Return over next N candles
- **Data needed**: Close prices only

### 4. Session Extreme
- **Logic**: Price at session high/low vs session open → mean reversion?
- **Outcome**: Next N candles from session extreme
- **Data needed**: High, Low, Close with session-aware grouping

### 5. Correlation Break
- **Logic**: Rolling correlation between two pairs breaks outside `std` bounds → reversion
- **Outcome**: Next-candle return of diverging pair
- **Data needed**: Close prices for two pairs

## Metrics

Each backtest run produces:

| Metric | Description |
|---|---|
| `total_signals` | Number of times signal fired in the data window |
| `win_rate` | % of forward lookaheads ending positive |
| `avg_return_pips` | Mean pips gained/lost per signal |
| `avg_win_pips` | Mean pips when signal was correct |
| `avg_loss_pips` | Mean pips when signal was wrong |
| `max_consecutive_wins` | Longest winning streak |
| `max_consecutive_losses` | Longest losing streak |
| `profit_factor` | Sum(winning returns) / Sum(losing returns) |

## Interface

Implemented as a Telegram command — no CLI needed:

```
/backtest EURUSD rsi_reversal D1
/backtest GBPUSD ma_cross H1
/backtest USDJPY atr_breakout H4 --threshold 30 --lookahead 5
```

The bot:
1. Downloads the requested parquet file (or uses cache)
2. Computes the signal condition vectorized across all bars
3. Walks forward N candles from each signal bar
4. Returns a formatted metric summary

Expected latency: 2-10 seconds per backtest (computation only, no API calls).

## File Structure (when implemented)

```
services/backtesting_service.py    # Backtest logic (vectorized per signal)
  ├── _rsi_reversal()
  ├── _atr_breakout()
  ├── _ma_cross()
  ├── _session_extreme()
  └── _correlation_break()

services/backtesting_templates.py  # Telegram formatting for results
```

## Anti-Scope

What this feature is NOT:
- No portfolio simulation, equity curves, or position sizing
- No walk-forward optimization or parameter sweeping
- No trade journal or persistent database
- No live trading or execution
- No ML models or predictions
