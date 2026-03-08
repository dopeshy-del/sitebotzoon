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
    REPORT_HOUR,
    REPORT_MINUTE,
    CHECK_INTERVAL,
)

logger = logging.getLogger(__name__)


async def check_balances(bot: Bot):
    """РџСЂРѕРІРµСЂРёС‚СЊ Р±Р°Р»Р°РЅСЃС‹ Рё РѕС‚РїСЂР°РІРёС‚СЊ Р°Р»РµСЂС‚ РµСЃР»Рё РЅСѓР¶РЅРѕ."""
    try:
        tw_balance = await tw.get_account_balance()
        if tw_balance.get("balance") is not None:
            if tw_balance["balance"] < TIMEWEB_BALANCE_THRESHOLD:
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    f"вљ пёЏ <b>Р’РЅРёРјР°РЅРёРµ!</b> Р‘Р°Р»Р°РЅСЃ TimeWeb: "
                    f"<b>{tw_balance['balance']} в‚Ѕ</b>\n"
                    f"РџРѕСЂРѕРі: {TIMEWEB_BALANCE_THRESHOLD} в‚Ѕ",
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
                    f"вљ пёЏ <b>Р’РЅРёРјР°РЅРёРµ!</b> Р‘Р°Р»Р°РЅСЃ PolzaAI: "
                    f"<b>{polzaai_balance['balance']} {polzaai_balance['currency']}</b>\n"
                    f"РџРѕСЂРѕРі: {POLZAAI_BALANCE_THRESHOLD}",
                    parse_mode="HTML"
                )
    except Exception as e:
        logger.error(f"PolzaAI balance check error: {e}")


async def check_servers(bot: Bot):
    """РџСЂРѕРІРµСЂРёС‚СЊ СЃС‚Р°С‚СѓСЃС‹ СЃРµСЂРІРµСЂРѕРІ."""
    try:
        servers = await tw.get_servers()
        for s in servers:
            if s["status"] not in ("on", "active"):
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    f"рџ”ґ <b>РЎРµСЂРІРµСЂ РЅРµРґРѕСЃС‚СѓРїРµРЅ!</b>\n"
                    f"РРјСЏ: <b>{s['name']}</b>\n"
                    f"IP: <code>{s['ip']}</code>\n"
                    f"РЎС‚Р°С‚СѓСЃ: {s['status']}",
                    parse_mode="HTML"
                )
    except Exception as e:
        logger.error(f"Server check error: {e}")


async def send_daily_report(bot: Bot):
    """РћС‚РїСЂР°РІРёС‚СЊ РµР¶РµРґРЅРµРІРЅС‹Р№ СЃРІРѕРґРЅС‹Р№ РѕС‚С‡С‘С‚."""
    try:
        import asyncio
        tw_bal, polzaai_bal, indexing, queries = await asyncio.gather(
            tw.get_account_balance(),
            polza.get_balance(),
            yx.get_indexing_stats(),
            yx.get_search_queries(),
        )
        text = fmt.fmt_full_report(tw_bal, polzaai_bal, indexing, queries)
        await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Daily report error: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # РџСЂРѕРІРµСЂРєР° Р±Р°Р»Р°РЅСЃРѕРІ РєР°Р¶РґС‹Рµ N РјРёРЅСѓС‚
    scheduler.add_job(
        check_balances,
        trigger="interval",
        minutes=CHECK_INTERVAL,
        args=[bot],
        id="check_balances",
    )

    # РџСЂРѕРІРµСЂРєР° СЃРµСЂРІРµСЂРѕРІ РєР°Р¶РґС‹Рµ 10 РјРёРЅСѓС‚
    scheduler.add_job(
        check_servers,
        trigger="interval",
        minutes=10,
        args=[bot],
        id="check_servers",
    )

    # Р•Р¶РµРґРЅРµРІРЅС‹Р№ РѕС‚С‡С‘С‚
    scheduler.add_job(
        send_daily_report,
        trigger="cron",
        hour=REPORT_HOUR,
        minute=REPORT_MINUTE,
        args=[bot],
        id="daily_report",
    )

    return scheduler
