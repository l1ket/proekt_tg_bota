from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message  # ReplyKeyboardRemove
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = [
        [
            KeyboardButton(text="Передать логин и пароль"),
            KeyboardButton(text="Получить оценки из АИС(дневника)"),
            KeyboardButton(text="Показать все команды")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Чтобы увидеть все команды пропишите /help"
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await message.answer(
        text="Привет этот бот получет много информации из электронного дневника свердловской области!\n"
        "Введите /help чтобы увидеть все команды.\nИли воспользуйтесь копками на клавиатуре.\nВерсия бота: v0.1.1(beta)", reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message(Command(commands=["help"]))
@router.message(F.text.lower() == "показать все команды")
async def cmd_help(message: Message):
    kb = [
        [
            KeyboardButton(text="Главное меню")
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Чтобы увидеть все команды пропишите /help"
    )
    await message.answer(
        text="Список доступных команд:\n"
        "/give - передать данные от аккаунта АИС,\n"
        "/give_allpars - передает данные об итоговых оценках.\n"
        "/this_week - передает данные об оценках за эту неделю.\n"
        "/polygodie_1 - передает данные об оценках за 1 полугодие.\n"
        "/polygodie_2 - передает данные об оценках за 2 полугодие(еще нет, потому что 2 полугодие не началось).\n",
        reply_markup=keyboard
    )


@router.message(Command(commands=["main"]))
@router.message(F.text.lower() == "главное меню")
async def cmd_main(message: Message):
    kb = [
        [
            KeyboardButton(text="Передать логин и пароль"),
            KeyboardButton(text="Получить оценки из АИС(дневника)"),
            KeyboardButton(text="Показать все команды")
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Версия бота: v0.1(beta)\nЧтобы увидеть все команды пропишите /help"
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await message.answer(
        text="Главное меню",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    builder = InlineKeyboardBuilder()
    builder.button(text="Эта неделя", callback_data='this_week_grades')
    builder.button(text="Домашние задания", callback_data='homeworks')
    builder.button(text="Первое полугодие", callback_data='1polygodie')
    builder.button(text="Второе полугодие", callback_data='2polygodie')
    builder.button(text="Итоговые оценки", callback_data='all_grades')
    builder.button(text="Получить все оценки по конкретному предмету(в разработке...)", callback_data='all_grades_for_lesson')
    builder.adjust(1)

    await callback.message.answer(
        text="Выберите вариант ниже:", reply_markup=builder.as_markup()
        )


@router.message(F.text.lower() == "получить оценки из аис(дневника)")
async def after_main(message: Message):
    builder = InlineKeyboardBuilder()

    builder.button(text="Эта неделя", callback_data='this_week_grades')
    builder.button(text="Домашние задания", callback_data='homeworks')
    builder.button(text="Первое полугодие", callback_data='1polygodie')
    builder.button(text="Второе полугодие", callback_data='2polygodie')
    builder.button(text="Итоговые оценки", callback_data='all_grades')
    builder.button(text="Получить все оценки по конкретному предмету(в разработке...)", callback_data='all_grades_for_lesson')

    builder.adjust(1)
    await message.answer(
        text="Выберите вариант ниже:", reply_markup=builder.as_markup()
        )


@router.message(Command("random"))
async def cmd_random(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup()
    )


# default_state - это то же самое, что и StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    kb = [
        [
            KeyboardButton(text="Главное меню")
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Чтобы увидеть все команды пропишите /help"
    )
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=keyboard
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    kb = [
        [
            KeyboardButton(text="Главное меню")
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Чтобы увидеть все команды пропишите /help"
    )
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=keyboard
    )
