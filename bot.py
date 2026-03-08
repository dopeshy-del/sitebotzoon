import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN_CHAT_ID
from handlers.main import router
from scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    # Запуск планировщика
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler started")

    # Уведомить о запуске
    try:
        await bot.send_message(ADMIN_CHAT_ID, "✅ <b>Бот запущен</b>", parse_mode="HTML")
    except Exception:
        pass

    logger.info("Bot started, polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
