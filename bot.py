import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import common, getting_log_and_pass


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token='')

    dp.include_router(common.router)
    dp.include_router(getting_log_and_pass.router)
    # сюда импортируйте ваш собственный роутер для напитков

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
