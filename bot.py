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

    await bot.delete_webhook(drop_pending_updates=True)  # Скипает все новые сообщения
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
"""
Конструкция 'если имя == мейн'
используеться для того чтобы проверить является ли файл основным исполнителем,
или его импортировали и используют.(это если простыми словами)
если не использовать эту конструкцию то при импорте запустится весь код
и это может помешать или вызвать какие-то ненужные сообщения.
(хотя в данном файле ее можно было не вставлять т.к. я буду всегда запускать его как основной)

"""
