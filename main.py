import asyncio
import logging
from logger import logger

from aiogram import Dispatcher, Bot

from routers.admin import admin_router
from routers.command import command_router
from routers.events import event_router
from routers.publication_schedule import publication_schedule_router
from routers.thematic_blocks import thematic_blocks_router

dp = Dispatcher()
bot = Bot(token="6830235739:AAG0Bo5lnabU4hDVWlhPQmLtiMVePI2xRGg")

dp.include_router(command_router)
dp.include_router(thematic_blocks_router)
dp.include_router(publication_schedule_router)
dp.include_router(admin_router)
dp.include_router(event_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Stop bot")


if __name__ == "__main__":
    asyncio.run(main())
