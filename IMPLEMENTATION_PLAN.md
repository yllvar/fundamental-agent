# Forex Fundamental Agent — Implementation Plan

## Current State

The project is a working economic news pipeline that:
1. Detects events from yfinance data (stock/indices moves)
2. Runs agents (Strands framework) to write articles, generate charts
3. Sends results via Telegram

**Two parallel codebases exist**, which is the root of complexity:
- `agents/` — newer Strands agent framework (message-passing, shared memory, orchestrator)
- `agents_backup/` — legacy orchestrator (used by `main.py`, `streamlit_app/app.py`)
- `main.py` uses the legacy path → `agents_backup/` → `event_detection_slack_system.py`

---

## Phase 0 — Unify + Clean (Day 1)

### Goal
Single codebase, single entry point, no Slack references.

### Changes

**Delete** (10 dead files — no longer importable):
| File | Why dead |
|---|---|
| `comprehensive_economic_monitor.py` | `notifications.slack_notifier` deleted |
| `comprehensive_economic_monitor_fixed.py` | Same |
| `comprehensive_economic_monitor_final.py` | Same |
| `run_complete_news_system.py` | Slack + old pipeline |
| `create_working_webhook.py` | Slack utility |
| `fix_orchestrator_import.py` | Fix script for old import |
| `test_full_automation.py` | Old test harness |
| `test_simple_automation.py` | Old test harness |
| `test_comprehensive_monitor.py` | Old test |
| `run_integrated_dashboard.py` | Slack refs |
| `test_integrated_dashboard.py` | Slack refs |

**Modify** `streamlit_ai_article_generator.py` — Remove `send_pdf_to_slack()` and Slack UI section.

**Modify** `run_complete_system.py` — Strip remaining Slack references:
- Replace `SlackIntegratedMonitor` import with `IntegratedMonitor`
- Replace `_get_slack_monitor()` with `_get_telegram_notifier()`
- Remove `slack-only` mode
- Remove `SLACK_WEBHOOK_URL` reads

**Modify** `agents_backup/orchestrator_agent.py` — Remove `from event_detection_slack_system import ...` (replaced with direct Telegram call in Phase 1).

**Modify** `main.py` — Switch from legacy orchestrator to Strands orchestrator:
- Before: `main.py → agents_backup.orchestrator_agent.OrchestratorAgent`
- After: `main.py → agents.orchestrator_strand.main_orchestrator`
- Same flow: detect events → for each → process → notify
- Output: same JSON/HTML files, same Telegram notifications

**Verify**: `main.py --mode full` runs end-to-end with Strands, Telegram notifications work, no errors.

---

## Phase 1 — Forex Data (Days 2-4)

### 1a. Forex Factory Scraper — `data_monitoring/forex_factory.py`

A single class:
```
ForexFactoryScraper
  - fetch_calendar(range="week") → list of event dicts
  - get_historical(event_id) → historical data for that event
  - _load_cache(date) / _save_cache(date, html)
```

**No over-engineering**: Simple aiohttp GET + BeautifulSoup. Cache to local file with 10-minute TTL.

Event schema:
```python
{
    "id": "12345",                # Forex Factory event ID
    "datetime": "2026-06-05T12:30:00Z",
    "currency": "USD",
    "event": "Non-Farm Employment Change",
    "impact": 3,                  # 1-3 stars
    "actual": None,               # "275K" or None if upcoming
    "forecast": "240K",
    "previous": "228K",
    "description": "..."
}
```

### 1b. Finnhub Calendar — `data_monitoring/finnhub_calendar.py`

A single class, same schema:
```
FinnhubCalendar
  - fetch_economic_calendar(from_date, to_date) → list of event dicts
```

**No over-engineering**: Single API call, parse JSON to same schema. Finnhub is backup — only used if Forex Factory fails or as supplement.

### 1c. Forex Config — `config/forex_config.py`

Simple dict, no classes:
```python
FOREX_PAIRS = {
    "EURUSD=X": {"name": "EUR/USD", "pip": 0.0001, "cb": "ECB"},
    ...
}
EVENT_TO_CURRENCY = {"NFP": "USD", "ECB rate decision": "EUR", ...}
```

### 1d. Extend Data Collector — `data_monitoring/data_collector.py`

Add one method: `get_forex_data(pair, period, interval)` — just yfinance with forex pair symbol.

Extend monitored symbols in `config/default.json` to include forex pairs.

### What this enables
After Phase 1, the system can:
- Fetch upcoming forex events from Forex Factory (cached)
- Fetch forex pair price data from yfinance
- Know which events affect which currencies

---

## Phase 2 — Forex Event Detection + Signals (Days 4-5)

### 2a. Extend Event Detector

Add forex-specific event types to `data_monitoring/event_detector.py`:
- `RATE_DECISION`, `CPI_MISS`, `NFP_SURPRISE`, `DOLLAR_SHIFT`
- Thresholds in pips (e.g., EUR/USD move > 50 pips = event)
- Pre/post event analysis window

**No over-engineering**: Same rule-based detection as current system, just new thresholds.

### 2b. Create Forex Analyst Strand — `agents/forex_analyst_strand.py`

A new Strand agent (follows same pattern as existing agents):
```
ForexAnalystStrand
  - process(context) → shared_memory["forex_analysis"]
  
Analyzes:
  - Event impact probability (from historical patterns)
  - Pre-event positioning (from yfinance rate data)
  - Cross-currency correlation
  - Fundamental score (rate differential, inflation, growth, trade)
```

**No over-engineering**: Single LLM call with structured JSON output. Template-based analysis if LLM fails.

### 2c. Add to Orchestrator Workflow

Insert `forex_analyst` into the Strands workflow list, between `data_analyst` and `article_writer`.

---

## Phase 3 — Query System (Days 6-9)

### 3a. Query Router — `forex_query_router.py`

**No over-engineering**: A single function, not a class with inheritance:

```python
async def route_query(query: str, user_id: str, context: dict) -> dict:
    """
    1. Classify intent with tiny DeepSeek call (~80 tokens)
    2. Extract entities (pair, event, timeframe)
    3. Return {"intent": "outlook", "pairs": ["EUR/USD"], ...}
    """
```

Supported intents: `outlook`, `event_analysis`, `risk_assessment`, `comparison`, `what_changed`, `confidence`, `historical`

### 3b. Conversation Agent — `agents/conversation_agent.py`

A Strand agent (same pattern as others):
```
ConversationStrand
  - process(context) → response dict
  
  Flow:
    1. route_query(query) → intent + entities
    2. Check cache → if hit, return cached
    3. Fetch relevant data (forex data, events)
    4. DeepSeek call with short system prompt → JSON response
    5. Format response to Telegram HTML
    6. Cache result
```

### 3c. Report Generator — `forex_report_generator.py`

Lightweight templates that convert JSON → Telegram HTML.

**No over-engineering**: Just string formatting, no template engine.

### 3d. Response Formatter — `response_formatter.py`

Formats the structured JSON output from DeepSeek into Telegram HTML messages.

**Zero LLM tokens** for formatting — pure string manipulation.

### LLM Call Design (Token Frugal)

Each query uses at most 2 LLM calls:
1. **Intent classification**: ~80 tokens system + query (~15 tokens) = ~95 total
2. **Analysis generation**: ~300 tokens context + query = ~400 total. **JSON mode** (6-10 fields max)

Cache hit = 0 LLM calls. Expected hit rate: 50%+ for repeated queries.

**No streaming, no verbose prompts, no chain-of-thought unless needed.**

Custom system prompt for each intent, not a single giant system prompt.

---

## Phase 4 — Telegram Query Handling (Days 9-10)

### 4a. Incoming Message Polling

Add to `notifications/telegram_notifier.py`:
```python
async def get_updates(self, offset: int = 0) -> list:
    """Poll Telegram for new messages"""
```

Run as a background task in `main.py`:
```python
asyncio.create_task(poll_telegram_queries())
```

### 4b. Conversation Manager — `conversation_manager.py`

Simple dict-based, not a database:
```python
{
    user_id: {
        "history": [{"role": "user/assistant", "content": "...", "timestamp": ...}],
        "preferences": {"pairs": ["EUR/USD"]},
        "last_active": datetime
    }
}
```

Pruning: keep last 5 exchanges, summarize and drop older ones.

**No over-engineering**: Not SQLite, not Redis, not a message queue. Just a dict + periodic cleanup.

---

## Phase 5 — Memory + Cache (Days 10-11)

### 5a. Cache Layer — `memory/analysis_cache.py`

File-based JSON cache, keyed by hash:
```
cache/{hash(pair + intent + date_hour)}.json  → 1h TTL
cache/{hash(pair + intent + date)}.json        → 24h TTL
```

**No over-engineering**: Not Redis, not SQLite. Simple file TTL check on read.

### 5b. Health Checks — `system/health_checks.py`

Single function, not a class:
```python
async def check_health() -> dict:
    """Return status of all data sources and agents"""
```

Called periodically by `main.py`.

---

## New File Summary

| File | Lines | Purpose |
|---|---|---|
| `config/forex_config.py` | 80 | Forex pair/event config |
| `data_monitoring/forex_factory.py` | 300 | Forex Factory scraper |
| `data_monitoring/finnhub_calendar.py` | 150 | Finnhub economic calendar |
| `agents/forex_analyst_strand.py` | 250 | Forex analysis Strand agent |
| `forex_query_router.py` | 180 | Intent classification + entity extraction |
| `agents/conversation_agent.py` | 300 | Query handling Strand agent |
| `forex_report_generator.py` | 200 | Report templates |
| `response_formatter.py` | 150 | Telegram HTML formatting |
| `conversation_manager.py` | 180 | User conversation state |
| `memory/analysis_cache.py` | 120 | File-based cache |
| `system/health_checks.py` | 150 | Data source health |

**Total new code: ~2,060 lines** (not 10,500+ as earlier naive estimate)

**Files modified:** ~8 existing files (~400 lines changed)
**Files deleted:** ~15

---

## Entry Point Simplification

After all phases, only ONE entry point:

```
main.py --mode full          # Full pipeline (scheduled run)
main.py --mode monitor       # Start monitoring + Telegram polling loop
main.py --mode single        # Single analysis run
main.py --mode health        # Health check
main.py --mode dashboard     # Streamlit dashboard
```

No more `run_full_pipeline.py`, `run_complete_system.py`, `run_integrated_dashboard.py`, etc.

---

## Token Budget (per article vs per query)

| Operation | LLM Calls | Tokens In | Tokens Out | Cost |
|---|---|---|---|---|
| Article generation | 1 | ~2,000 | ~1,500 | ~2.5¢ |
| Query (cache hit) | 0 | 0 | 0 | 0¢ |
| Query (intent only) | 1 | ~95 | ~30 | ~0.01¢ |
| Query (full analysis) | 2 | ~500 | ~200 | ~0.05¢ |
| Daily query budget (100 queries, 50% cached) | 50 | ~25K | ~10K | ~2.5¢ |

---

## What We're NOT Building (to avoid over-engineering)

| NOT building | Reason |
|---|---|
| Database (SQLite, Postgres) | File storage is sufficient for single-user |
| Web framework (FastAPI, Flask) | Telegram is the UI |
| Authentication | Single-user Telegram bot |
| Retry queues | Simple retry with backoff in the caller |
| Metrics collection | Health checks give us what we need |
| Plugin system | All agents are hardcoded in Strands workflow |
| Async task queue | asyncio is sufficient for single-bot concurrency |
| ORM | Not needed for file-based storage |
| CI/CD pipeline changes | Existing CI tests still pass |
| Container orchestration | Railway deploy stays same |
