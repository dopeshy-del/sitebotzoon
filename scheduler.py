import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import api.timeweb as tw
import api.polzaai as polza
import api.yandex_webmaster as yx
import api.cursor as cursor
import formatters as fmt
from config import (
    ADMIN_CHAT_ID,
    TIMEWEB_BALANCE_THRESHOLD,
    TIMEWEB_RUNWAY_HOURS_THRESHOLD,
    POLZAAI_BALANCE_THRESHOLD,
    REPORT_HOUR,
    REPORT_MINUTE,
    CHECK_INTERVAL,
    CURSOR_ENABLED,
    CURSOR_REMAINING_THRESHOLD,
    CURSOR_CHECK_INTERVAL,
)

logger = logging.getLogger(__name__)
_seen_cursor_runs: set[str] = set()


async def check_balances(bot: Bot):
    """Проверить балансы и отправить алерт если нужно."""
    try:
        tw_balance = await tw.get_account_balance()
        if tw_balance.get("balance") is not None:
            balance = tw_balance["balance"]
            runway_days = tw_balance.get("runway_days")
            runway_hours = runway_days * 24 if runway_days is not None else None

            low_balance = balance <= TIMEWEB_BALANCE_THRESHOLD
            low_runway = runway_hours is not None and runway_hours <= TIMEWEB_RUNWAY_HOURS_THRESHOLD

            if low_balance or low_runway:
                reasons = []
                if low_balance:
                    reasons.append(f"Порог баланса: {TIMEWEB_BALANCE_THRESHOLD} ₽")
                if low_runway:
                    reasons.append(f"Порог остатка жизни: {TIMEWEB_RUNWAY_HOURS_THRESHOLD} ч")

                runway_line = ""
                if runway_hours is not None:
                    runway_line = f"\nОсталось жить: <b>{round(runway_hours, 1)} ч</b>"

                await bot.send_message(
                    ADMIN_CHAT_ID,
                    f"⚠️ <b>Внимание!</b> Баланс TimeWeb: "
                    f"<b>{balance} ₽</b>{runway_line}\n"
                    f"Сработало: {'; '.join(reasons)}",
                    parse_mode="HTML"
                )
    except Exception as e:
        logger.error(f"TimeWeb balance check error: {e}")

    try:
        polzaai_balance = await polza.get_balance()
        if polzaai_balance.get("balance") is not None:
            if polzaai_balance["balance"] < POLZAAI_BALANCE_THRESHOLD:
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    f"⚠️ <b>Внимание!</b> Баланс PolzaAI: "
                    f"<b>{polzaai_balance['balance']} {polzaai_balance['currency']}</b>\n"
                    f"Порог: {POLZAAI_BALANCE_THRESHOLD}",
                    parse_mode="HTML"
                )
    except Exception as e:
        logger.error(f"PolzaAI balance check error: {e}")


async def check_cursor(bot: Bot):
    """Проверка Cursor: остаток лимита и завершение задач."""
    try:
        limits = await cursor.get_limits()
        remaining = limits.get("remaining")
        if remaining is not None and remaining <= CURSOR_REMAINING_THRESHOLD:
            await bot.send_message(
                ADMIN_CHAT_ID,
                (
                    "⚠️ <b>Cursor: низкий остаток лимита</b>\n"
                    f"Остаток: <b>{remaining}</b>\n"
                    f"Порог: {CURSOR_REMAINING_THRESHOLD}"
                ),
                parse_mode="HTML",
            )
    except Exception as e:
        logger.error(f"Cursor limits check error: {e}")

    try:
        runs_payload = await cursor.get_recent_runs(limit=20)
        runs = runs_payload.get("runs", [])
        for run in runs:
            run_id = run.get("id")
            if not run_id or run_id in _seen_cursor_runs:
                continue

            status = (run.get("status") or "unknown").lower()
            if status in {"completed", "done", "succeeded", "failed", "error", "cancelled"}:
                _seen_cursor_runs.add(run_id)
                icon = "✅" if status in {"completed", "done", "succeeded"} else "❌"
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    (
                        f"{icon} <b>Cursor задача завершена</b>\n"
                        f"ID: <code>{run_id}</code>\n"
                        f"Статус: <b>{status}</b>\n"
                        f"Промпт: {run.get('prompt', '—')}"
                    ),
                    parse_mode="HTML",
                )
    except Exception as e:
        logger.error(f"Cursor runs check error: {e}")


async def check_servers(bot: Bot):
    """Проверить статусы серверов."""
    try:
        servers = await tw.get_servers()
        for s in servers:
            if s["status"] not in ("on", "active"):
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    f"🔴 <b>Сервер недоступен!</b>\n"
                    f"Имя: <b>{s['name']}</b>\n"
                    f"IP: <code>{s['ip']}</code>\n"
                    f"Статус: {s['status']}",
                    parse_mode="HTML"
                )
    except Exception as e:
        logger.error(f"Server check error: {e}")


async def send_daily_report(bot: Bot):
    """Отправить ежедневный сводный отчёт."""
    try:
        import asyncio
        tw_bal, tw_products, polzaai_bal, polza_usage, indexing, queries = await asyncio.gather(
            tw.get_account_balance(),
            tw.get_products_summary(),
            polza.get_balance(),
            polza.get_usage_stats(),
            yx.get_indexing_stats(),
            yx.get_search_queries(),
        )
        text = fmt.fmt_full_report(tw_bal, tw_products, polzaai_bal, polza_usage, indexing, queries)
        await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Daily report error: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # Проверка балансов каждые N минут
    scheduler.add_job(
        check_balances,
        trigger="interval",
        minutes=CHECK_INTERVAL,
        args=[bot],
        id="check_balances",
    )

    if CURSOR_ENABLED:
        scheduler.add_job(
            check_cursor,
            trigger="interval",
            minutes=CURSOR_CHECK_INTERVAL,
            args=[bot],
            id="check_cursor",
        )

    # Проверка серверов каждые 10 минут
    scheduler.add_job(
        check_servers,
        trigger="interval",
        minutes=10,
        args=[bot],
        id="check_servers",
    )

    # Ежедневный отчёт
    scheduler.add_job(
        send_daily_report,
        trigger="cron",
        hour=REPORT_HOUR,
        minute=REPORT_MINUTE,
        args=[bot],
        id="daily_report",
    )

    return scheduler
