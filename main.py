import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.config import BOT_TOKEN
from handlers import other_handlers, user_handlers
from keyboards.main_menu import set_main_menu
from scripts.setup_db import setup_db

# Initialize the logger
logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # We output information about the start of the bot launch to the console
    logger.info('Starting bot')

    # todo: WARNING: This will delete all existing tables and will
    # re-fill the data for the bot's lexicon. See docstring
    setup_db()

    # Initialize the bot and dispatcher
    bot: Bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Setting up the main menu of the bot
    await set_main_menu(bot)

    # We register routers in the manager
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await set_main_menu(bot)

    # Skip the accumulated updates and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
