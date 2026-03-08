import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import api.timeweb as tw
import api.polzaai as polza
import api.yandex_webmaster as yx
import formatters as fmt
from config import (
    ADMIN_CHAT_ID,
    TIMEWEB_BALANCE_THRESHOLD,
    POLZAAI_BALANCE_THRESHOLD,
    TIMEWEB_BALANCE_ALERTS_ENABLED,
    REPORT_HOUR,
    REPORT_MINUTE,
    CHECK_INTERVAL,
)

logger = logging.getLogger(__name__)


async def check_balances(bot: Bot):
    """Проверить балансы и отправить алерт если нужно."""
    try:
        if TIMEWEB_BALANCE_ALERTS_ENABLED:
            tw_balance = await tw.get_account_balance()
            if tw_balance.get("balance") is not None:
                if tw_balance["balance"] < TIMEWEB_BALANCE_THRESHOLD:
                    await bot.send_message(
                        ADMIN_CHAT_ID,
                        f"⚠️ <b>Внимание!</b> Баланс TimeWeb: "
                        f"<b>{tw_balance['balance']} ₽</b>\n"
                        f"Порог: {TIMEWEB_BALANCE_THRESHOLD} ₽",
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
