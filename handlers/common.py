from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message  # ReplyKeyboardRemove
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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


@router.message(F.text.lower() == "получить оценки из аис(дневника)")
async def after_main(message: Message):
    kb = [
        [
            KeyboardButton(text="Первое полугодие"),
            KeyboardButton(text="Эта неделя"),
            KeyboardButton(text="Итоговые оценки"),
            KeyboardButton(text="Второе полугодие"),
            KeyboardButton(text="Получить все оценки по конкретному предмету"),
            KeyboardButton(text="Главное меню")
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
        text="Выберите вариант на клавиатуре или напшите сами один из следующих вариантов:\n"
        "1. Первое полугодие\n2. Эта неделя\n3. Итоговые оценки\n4. Второе полугодие", reply_markup=builder.as_markup(resize_keyboard=True)
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
