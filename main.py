#!/usr/bin/env python3
"""
Fundamental Agent — Main entry point
Modes: full, monitor, single, health, dashboard
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from config.settings import load_config
from agents.orchestrator_strand import main_orchestrator, StrandContext
from notifications.telegram_notifier import TelegramNotifier, AlertPriority
from event_detection_slack_system import EventMonitoringSystem
from agents.conversation_agent import ConversationStrand
from conversation_manager import ConversationManager
from response_formatter import format_help_message, format_error_message
from system.health_checks import check_health as run_health_check
from services.scheduler import run_scheduler


def setup_logging(log_level: str = "INFO"):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"fundamental_agent_{datetime.now().strftime('%Y%m%d')}.log")
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


async def run_full_pipeline(max_articles: int = 3):
    """Detect events, process through Strands, notify via Telegram"""
    logger = logging.getLogger(__name__)

    event_monitor = EventMonitoringSystem()
    scan_result = event_monitor.run_single_scan()
    events = scan_result.get('events', [])

    if not events:
        print("No events detected")
        return []

    print(f"Processing {min(len(events), max_articles)} event(s)...")
    results = []

    tg = TelegramNotifier(
        os.getenv('TELEGRAM_BOT_TOKEN', ''),
        os.getenv('TELEGRAM_CHAT_ID', '')
    ) if os.getenv('TELEGRAM_BOT_TOKEN') else None

    for i, ev in enumerate(events[:max_articles]):
        symbol = ev.get('symbol', 'Unknown')
        logger.info(f"Processing {i+1}/{len(events[:max_articles])}: {symbol}")

        event = {
            'symbol': symbol,
            'event_type': ev.get('type', 'unknown'),
            'severity': ev.get('severity', 'low'),
            'description': ev.get('title', ev.get('description', '')),
            'change_percent': ev.get('change_percent', 0),
            'timestamp': ev.get('timestamp', datetime.now().isoformat()),
        }

        try:
            context = StrandContext(
                strand_id=f"main_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                input_data={'event': event}
            )
            result = await main_orchestrator.process(context)
            results.append(result)

            if tg:
                package = result.get('package', {})
                article = package.get('article', {})
                review = package.get('review_result', {})
                text = (
                    f"\U0001f4f0 <b>Article: {symbol}</b>\n"
                    f"{article.get('lead', event.get('description', ''))[:200]}"
                )
                await tg._send_telegram(text)

            print(f"  {symbol}: {result.get('execution_time', 0):.0f}s | quality: {package.get('metadata', {}).get('quality_score', 'N/A')}/10")

        except Exception as e:
            logger.error(f"Failed to process {symbol}: {e}")
            print(f"  {symbol}: FAILED - {e}")

    print(f"\nPipeline complete: {len(results)} article(s) generated")
    return results


async def run_scheduled_mode(interval_hours: int = 1):
    """Run pipeline on a schedule"""
    print(f"Scheduled mode: running every {interval_hours} hour(s)")
    while True:
        await run_full_pipeline()
        await asyncio.sleep(interval_hours * 3600)


async def poll_telegram_queries(tg: TelegramNotifier, conv_mgr: ConversationManager, chat_id: str):
    """Poll Telegram for incoming forex queries and respond"""
    logger = logging.getLogger(__name__)
    conv_agent = ConversationStrand()
    offset = 0

    while True:
        try:
            updates = await tg.get_updates(offset)
            for update in updates:
                update_id = update.get("update_id", 0)
                offset = update_id + 1

                msg = update.get("message", {})
                text = msg.get("text", "").strip()
                user_id = str(msg.get("from", {}).get("id", ""))
                msg_chat_id = str(msg.get("chat", {}).get("id", ""))

                if msg_chat_id != chat_id:
                    continue
                if not text or text.startswith("/"):
                    if text == "/start" or text == "/help":
                        await tg.send_message(format_help_message())
                    continue

                logger.info(f"Telegram query: {text[:80]}...")

                context = StrandContext(
                    strand_id=f"query_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    input_data={"query": text, "user_id": user_id}
                )

                try:
                    result = await conv_agent.process(context)
                    response = result.get("response_text", "")
                    if not response:
                        response = "Sorry, I couldn't analyze that."
                    await tg.send_message(response)
                    conv_mgr.add_exchange(user_id, text, response)
                except Exception as e:
                    logger.error(f"Query failed: {e}")
                    await tg.send_message(format_error_message(text, str(e)))

                await asyncio.sleep(0.5)

            conv_mgr.cleanup_idle()

        except Exception as e:
            logger.error(f"Polling error: {e}")
            await asyncio.sleep(5)

        await asyncio.sleep(1)


async def run_monitor_mode():
    """Event-driven monitoring — no continuous polling"""
    print("Monitor mode started. Events: market opens | user queries | economic calendar")
    tg = TelegramNotifier(
        os.getenv('TELEGRAM_BOT_TOKEN', ''),
        os.getenv('TELEGRAM_CHAT_ID', '')
    ) if os.getenv('TELEGRAM_BOT_TOKEN') else None

    if not tg:
        print("Telegram not configured — monitor mode requires TELEGRAM_BOT_TOKEN")
        return

    conv_mgr = ConversationManager()

    tasks = [
        asyncio.create_task(poll_telegram_queries(tg, conv_mgr, os.getenv('TELEGRAM_CHAT_ID', ''))),
        asyncio.create_task(run_scheduler(tg)),
    ]
    await asyncio.gather(*tasks)


def check_health():
    """Check system health"""
    result = asyncio.run(run_health_check())
    print("System Health Check")
    print(f"  Time: {result.get('timestamp', '?')}")
    print(f"  DeepSeek API: {result.get('deepseek_api', {}).get('status', '?')}")
    print(f"  Telegram: {result.get('telegram', {}).get('status', '?')}")
    print(f"  Yahoo Finance: {result.get('yahoo_finance', {}).get('status', '?')}")
    print(f"  Forex Pairs: {result.get('forex_config', {}).get('pairs_configured', 0)}")
    print(f"  Cache: {result.get('cache', {}).get('entries', 0)} entries, {result.get('cache', {}).get('size_bytes', 0)} bytes")
    ok = result.get('all_ok', False)
    print(f"  Overall: {'OK' if ok else 'ISSUES DETECTED'}")


def main():
    parser = argparse.ArgumentParser(description="Fundamental Agent")
    parser.add_argument("--mode", choices=["full", "monitor", "single", "schedule", "health"],
                       default="full", help="Execution mode")
    parser.add_argument("--config", default="config/default.json", help="Config path")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Log level")
    parser.add_argument("--api-key", help="Override DEEPSEEK_API_KEY")
    parser.add_argument("--max-articles", type=int, default=3, help="Max articles per run")
    parser.add_argument("--interval", type=int, default=1, help="Schedule interval (hours)")

    args = parser.parse_args()
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    if args.api_key:
        os.environ['DEEPSEEK_API_KEY'] = args.api_key

    try:
        config = load_config(args.config)
        logger.info(f"Config loaded: {args.config}")

        if args.mode == "full":
            asyncio.run(run_full_pipeline(max_articles=args.max_articles))

        elif args.mode == "schedule":
            asyncio.run(run_scheduled_mode(interval_hours=args.interval))

        elif args.mode == "monitor":
            asyncio.run(run_monitor_mode())

        elif args.mode == "single":
            result = asyncio.run(run_full_pipeline(max_articles=1))

        elif args.mode == "health":
            check_health()

        logger.info("Execution complete")

    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
