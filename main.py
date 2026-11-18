import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramServerError

from app.config import settings
from app.db import init_db
from app.handlers import router
from app.web import start_health_server


async def run_bot_with_retry(bot: Bot, dp: Dispatcher):
    """Telegram vaqtinchalik xato bersa, botni qayta ulashga urinadi."""
    retry_delay = 5
    max_retry_delay = 60
    allowed_updates = dp.resolve_used_update_types()

    while True:
        try:
            logging.info("Telegram bot polling boshlanmoqda...")
            await dp.start_polling(bot, allowed_updates=allowed_updates)
            # Polling odatiy tarzda to'xtatilsa, sikldan chiqamiz.
            break
        except (TelegramServerError, TelegramNetworkError, asyncio.TimeoutError) as exc:
            logging.warning(
                "Telegram bilan aloqa vaqtincha uzildi: %s. %s soniyadan keyin qayta uriniladi.",
                exc,
                retry_delay,
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_retry_delay)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan")

    # Ma'lumotlar bazasini ishga tushirish.
    await init_db()

    bot = Bot(
        settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    await start_health_server()

    try:
        await run_bot_with_retry(bot, dp)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
