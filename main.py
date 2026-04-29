from asyncio import run
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault

from data.config import BOT_TOKEN, ADMIN
from handlers import router
from data.loader import db, update_admins_cache, update_channels_cache
from middlewares.is_subscription import SubscriptionMiddleware


dp = Dispatcher()


@dp.startup()
async def startup_ans(bot:Bot):
    await db.db_start()
    await update_admins_cache()
    await update_channels_cache()
    try:
        await bot.send_message(ADMIN, "Bot started")
    except Exception as e:
        print(f"Adminga xabar yuborib bo'lmadi: {e}")
    

@dp.shutdown()
async def shutdown_ans(bot:Bot):
    try:
        await bot.send_message(ADMIN, "Bot stopped")
    except Exception as e:
        print(f"Adminga xabar yuborib bo'lmadi: {e}")


async def main():
    dp.include_router(router)
    dp.message.outer_middleware(SubscriptionMiddleware())
    dp.callback_query.outer_middleware(SubscriptionMiddleware())
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode = ParseMode.HTML), link_preview_is_disabled=True)
    await dp.start_polling(bot)

    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Botni qayta ishga tushirish")
        ],
        scope=BotCommandScopeDefault()
    )


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        run(main())
    except KeyboardInterrupt:
        pass