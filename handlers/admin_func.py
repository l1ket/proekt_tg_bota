import sqlite3
from aiogram import F, Router
from aiogram import Bot
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import default_state
from aiogram.types import Message  # ReplyKeyboardRemove
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

router = Router()
bot = Bot(token='6028764195:AAF1iMb6Vh_yYdJGnQsn73I3J1Vv4W-YoZc')

class admins_states(StatesGroup):
    choose = State()
    mes = State()


@router.message(Command(commands='admin'))
async def message_from_admin(message: Message):
    if message.from_user.id == 910526716:
        builder = InlineKeyboardBuilder()
        builder.button(text="Разослать всем сообщение",
                       callback_data='message_for_all')
        builder.button(text="Отмена", callback_data='...')
        builder.adjust(1)
        await message.answer(text='Привет, админ.',
                             reply_markup=builder.as_markup())
    else:
        await message.answer(text='В доступе отказано')


@router.callback_query(F.data == "message_for_all")
async def choose_message(callback: types.CallbackQuery,
                         state: FSMContext):
    await callback.answer(text='213')
    await callback.message.answer(
        text="Введите сообщение для всех",
        )
    await state.set_state(admins_states.choose)


@router.message(admins_states.choose)
async def send_messages(message: Message, state: FSMContext):
    ids = await get_ids()
    for us_id in ids:
        us_id = int(us_id)
        await bot.send_message(chat_id=us_id,
                               text=message.text)
    await message.answer(
        text="Сообщение отправленно",
        )
    await state.clear()


async def get_ids():
    ids = []
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM Users')
    results = cursor.fetchall()
    for i in results:
        for user_id in i:
            ids.append(user_id)
    connection.close()
    return ids


@router.message()  # Функция для ответа на любые не подохдящие сообщения
async def messages(message: Message):
    kb = [
        [
            KeyboardButton(text="Передать логин и пароль"),
            KeyboardButton(text="Получить оценки из АИС(дневника)")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Версия бота: v0.2(beta)"
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await message.answer(text='Я не понял, попробуйте потыкать по кнопкам',
                         reply_markup=builder.as_markup(resize_keyboard=True))
