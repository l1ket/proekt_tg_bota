from aiogram import Router, F

from aiogram.types import Message, ReplyKeyboardMarkup, \
    KeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()


@router.callback_query(F.data == "cancel")
async def cancell(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    kb = [
        [
            KeyboardButton(text="Аккаунты"),
            KeyboardButton(text="Получить информацию из АИС(дневника)")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await callback.message.answer(text='Главное меню',
        reply_markup=builder.as_markup(resize_keyboard=True))


@router.message()  # Функция для ответа на любые не подохдящие сообщения
async def messages(message: Message):
    kb = [
        [
            KeyboardButton(text="Аккаунты"),
            KeyboardButton(text="Получить информацию из АИС(дневника)")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await message.answer(text='Я не понял, попробуйте потыкать по кнопкам',
                         reply_markup=builder.as_markup(resize_keyboard=True))
