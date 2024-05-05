"""
Версия бота v0.3
"""

import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dannie import TOKEN
from handlersIO import common, getting_log_and_pass, \
    admin_func, other_message


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    main_login TEXT NOT NULL
    )
    ''')
    connection.commit()
    connection.close()

    connection = sqlite3.connect('accs_info.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    login_user TEXT NOT NULL,
    password_user TEXT NOT NULL
    )
    ''')
    connection.commit()
    connection.close()

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=TOKEN)

    dp.include_router(common.router)
    dp.include_router(getting_log_and_pass.router)
    dp.include_router(admin_func.router)
    dp.include_router(other_message.router)

    await bot.delete_webhook(
        drop_pending_updates=True
        )  # Скипает все новые сообщения
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
