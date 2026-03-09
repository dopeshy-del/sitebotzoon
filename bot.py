import asyncio
import logging
import fcntl
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramConflictError

from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN_CHAT_ID, INSTANCE_LOCK_FILE
from handlers.main import router
from scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class SingleInstanceLock:
    """Простой файловый lock, чтобы не запускать второй polling-процесс."""

    def __init__(self, lock_path: str):
        self.lock_path = Path(lock_path)
        self._fd = None

    def acquire(self) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fd = self.lock_path.open("w")
        try:
            fcntl.flock(self._fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False

        self._fd.write(str(Path("/proc/self").resolve().name))
        self._fd.flush()
        return True

    def release(self):
        if not self._fd:
            return
        try:
            fcntl.flock(self._fd.fileno(), fcntl.LOCK_UN)
        finally:
            self._fd.close()
            self._fd = None


async def main():
    lock = SingleInstanceLock(INSTANCE_LOCK_FILE)
    if not lock.acquire():
        logger.critical(
            "Обнаружен второй экземпляр бота. Останавливаю запуск, чтобы избежать TelegramConflictError."
        )
        return

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    # На всякий случай сбрасываем webhook перед long-polling
    await bot.delete_webhook(drop_pending_updates=False)

    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler started")

    try:
        await bot.send_message(ADMIN_CHAT_ID, "✅ <b>Бот запущен</b>", parse_mode="HTML")
    except Exception:
        pass

    logger.info("Bot started, polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except TelegramConflictError:
        logger.critical(
            "TelegramConflictError: одновременно запущено несколько polling-инстансов с тем же BOT_TOKEN."
        )
    finally:
        scheduler.shutdown()
        await bot.session.close()
        lock.release()


if __name__ == "__main__":
    asyncio.run(main())
