import os

from parsIO import AISdnevnik
from typing import Optional

from handlersIO.getting_log_and_pass import get_default_credentials, \
    check_acc_in_bd_accs, return_accs, return_main_login, \
    change_main_login

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, WebAppInfo, InputFile, InputMediaDocument, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.methods import SendMediaGroup

router = Router()


class MyCallback(CallbackData, prefix="my"):
    foo: str
    value: str
    page: Optional[int] = None


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
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

    await message.answer(
        text="Привет, этот бот имеет такие же функции как и дневник.\n"
        "Для продолжения воспользуйтесь копками на клавиатуре.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message(Command(commands=["main"]))
@router.message(F.text.lower() == "главное меню")
async def cmd_main(message: Message, state: FSMContext):
    await state.clear()
    kb = [
        [
            KeyboardButton(text="Аккаунты"),
            KeyboardButton(text="Получить информацию из АИС(дневника)"),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await message.answer(
        text="Главное меню",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


""" Аккаунты(начало)"""


@router.message(F.text.lower() == "аккаунты")
async def accs(message: Message, state: FSMContext):
    await state.clear()
    kb = [
        [
            KeyboardButton(text="Показать все аккаунты"),
            KeyboardButton(text="Добавить аккаунт"),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    await message.answer(
        text="Выберите действие",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message(F.text.lower() == "показать все аккаунты")
async def all_accs(message: Message, state: FSMContext):
    await state.clear()
    us_id = message.from_user.id

    if await check_acc_in_bd_accs(user_id=us_id) is not True:
        await message.answer(
            text='Для продолжения вы должны добавить хотя бы один аккаунт')
    else:

        accs = await return_accs(user_id=us_id)
        main_login = await return_main_login(user_id=us_id)
        builder = InlineKeyboardBuilder()

        for i in accs:
            login = i[0]
            password = i[1]
            account = await AISdnevnik(log=login, passw=password).accs_info()
            if main_login == login:
                builder.button(text=f"Основной: {account}",
                               callback_data=MyCallback(foo='accs', value=login))
            else:
                builder.button(text=account, callback_data=MyCallback(foo='accs', value=login))
        builder.adjust(1)
        await message.answer(
            text="Нажмите на кнопку чтобы выбрать аккаунт как основной",
            reply_markup=builder.as_markup()
        )


@router.callback_query(MyCallback.filter(F.foo == 'accs'))
async def chage_main(callback: types.CallbackQuery, callback_data: MyCallback):
    us_id = callback.from_user.id
    login = await return_main_login(user_id=us_id)

    kb = [
            [
                KeyboardButton(text="Аккаунты"),
                KeyboardButton(text="Получить информацию из АИС(дневника)"),
            ],
        ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    builder = ReplyKeyboardBuilder.from_markup(keyboard)
    builder.adjust(2)

    if callback_data.value == login:
        await callback.message.answer(
            text="Вы уже выбрали этот аккаунт как основной",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
        await callback.answer(text='Этот аккаунт уже основной.')
    else:

        await change_main_login(user_id=us_id, login=callback_data.value)
        await callback.message.delete()

        await callback.message.answer(
            text=f'Основной аккаунт изменен на {callback_data.value}',
            reply_markup=builder.as_markup(resize_keyboard=True)
            )


""" Аккаунты(конец)"""


@router.message(F.text.lower() == "получить информацию из аис(дневника)")
async def after_main(message: Message, state: FSMContext):
    await state.clear()
    us_id = message.from_user.id

    if await check_acc_in_bd_accs(user_id=us_id) is not True:
        await message.answer(
            text='Для продолжения вы должны добавить хотя бы один аккаунт')
    else:
        builder = InlineKeyboardBuilder()

        builder.button(text="Оценки", callback_data='grades')
        builder.button(text="Обьявления", callback_data='announcements')
        builder.button(text="Домашние задания", callback_data='homework')
        builder.button(text="test", callback_data='test')

        builder.adjust(2)
        await message.answer(
            text="Выберите интересующий вас пункт:", reply_markup=builder.as_markup()
            )


@router.callback_query(F.data == "test")
async def test(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    builder = InlineKeyboardBuilder()
    builder.button(text="Оценки", web_app=WebAppInfo(url='https://dnevnik.egov66.ru/login/'))

    builder.adjust(2)
    await callback.message.answer(
        text="Выберите любой вариант:", reply_markup=builder.as_markup()
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
        resize_keyboard=True
    )
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=keyboard
    )

""" Домашка(начало) """

@router.callback_query(F.data == "homework")
async def home(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)

    builder = InlineKeyboardBuilder()
    result = await AISdnevnik(log=log, passw=pasw).homework_info()
    mes = result[0]
    if result[1] != '0001-01-01':
        builder.button(text="Предыдущий день", callback_data=MyCallback(foo='works', value=result[1]))
    else:
        builder.button(text="Конец", callback_data="0")
    
    builder.button(text="Назад", callback_data='grades')

    if result[2] != '0001-01-01':
        builder.button(text="Следующий день", callback_data=MyCallback(foo='works', value=result[2]))
    else:
        builder.button(text="Конец", callback_data="0")      
    await callback.message.answer(text=mes, reply_markup=builder.as_markup())


@router.callback_query(MyCallback.filter(F.foo == 'works'))
async def childrens(callback: types.CallbackQuery, callback_data: MyCallback):
    await callback.answer()
    await callback.message.delete()

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)

    builder = InlineKeyboardBuilder()
    result = await AISdnevnik(log=log, passw=pasw).homework_info(date=callback_data.value)
    mes = result[0]
    if result[1] != '0001-01-01':
        builder.button(text="Предыдущий день", callback_data=MyCallback(foo='works', value=result[1]))
    else:
        builder.button(text="Конец", callback_data="0")
    
    builder.button(text="Назад", callback_data='grades')

    if result[2] != '0001-01-01':
        builder.button(text="Следующий день", callback_data=MyCallback(foo='works', value=result[2]))
    else:
        builder.button(text="Конец", callback_data="0")      
    await callback.message.answer(text=mes, reply_markup=builder.as_markup())

""" Домашка(конец) """


@router.callback_query(F.data == "announcements")
async def home(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)

    builder = InlineKeyboardBuilder()
    result = await AISdnevnik(log=log, passw=pasw).announcements()
    
    builder.button(text="Назад", callback_data='grades')
    try:
        await callback.message.answer(text=result[0], reply_markup=builder.as_markup())
        if result[1] is not None:
            for i in result[1]:
                file = FSInputFile(i)
                await callback.message.answer_document(document=file)
    except Exception as e:
        print(e)
        await callback.message.answer(text='Ошибка', reply_markup=builder.as_markup())
    finally:
        try:
            for i in result[1]:
                os.remove(i)
        except Exception as e:
            pass


@router.callback_query(F.data == "grades")
async def grades(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)

    builder = InlineKeyboardBuilder()
    result = await AISdnevnik(log=log, passw=pasw).return_periods()
    if isinstance(result, dict):
        for i in result.items():
            builder.button(text=i[0],
                        callback_data=MyCallback(foo='items', value=i[0]))

        builder.adjust(2)
        await callback.message.answer(
            text="Выберите любой вариант:", reply_markup=builder.as_markup()
            )
    elif isinstance(result, tuple):
        periods = result[0]
        text = result[1]

        for key, value in periods.items():
            builder.button(text=key,
                        callback_data=MyCallback(foo='children', value=value))
        builder.adjust(2)

        await callback.message.answer(
            text=text, reply_markup=builder.as_markup()
        )


@router.callback_query(MyCallback.filter(F.foo == 'children'))
async def childrens(callback: types.CallbackQuery, callback_data: MyCallback):
    await callback.answer()
    await callback.message.delete()

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)

    builder = InlineKeyboardBuilder()
    result = await AISdnevnik(log=log, passw=pasw).return_periods(children=callback_data.value)
    if isinstance(result, dict):
        for key, value in result.items():
            builder.button(text=key,
                        callback_data=MyCallback(foo='items', value=key))

        builder.adjust(2)
        await callback.message.answer(
            text="Выберите любой вариант:", reply_markup=builder.as_markup()
            )

    elif isinstance(result, tuple):
        periods = result[0]
        text = result[1]

        for key, value in periods.items():
            builder.button(text=key,
                        callback_data=MyCallback(foo='children', value=value))
        builder.adjust(2)

        await callback.message.answer(
            text=text, reply_markup=builder.as_markup()
        )


""" Дни недели"""


@router.callback_query(MyCallback.filter(F.foo == 'items'))
async def week_grade(callback: types.CallbackQuery, callback_data: MyCallback):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text="Поиск оценок...")

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)
    result = await AISdnevnik(log=log, passw=pasw).select_var(callback_data.value)

    if isinstance(result, str):
        builder = InlineKeyboardBuilder()
        builder.button(text="Назад", callback_data='grades')
        builder.adjust(1)
        await callback.message.answer(text=result, reply_markup=builder.as_markup())

    elif isinstance(result, tuple):
        text = result[0]
        next_page = result[1]
        previous_page = result[2]
        page = result[3]

        if next_page is True:
            next_page = page + 1
        if previous_page is True:
            previous_page = page - 1

        builder = InlineKeyboardBuilder()

        if previous_page is False:
            builder.button(text='Конец', callback_data='end')
        else:
            builder.button(text='Предыдущая неделя', callback_data=MyCallback(foo='previous', value=callback_data.value, page=previous_page))
        if next_page is False:
            builder.button(text='Конец', callback_data='end')
        else:
            builder.button(text='Следующая неделя', callback_data=MyCallback(foo='next', value=callback_data.value, page=next_page))

        builder.button(text="Назад", callback_data='grades')
        builder.adjust(2)

        await callback.message.answer(text=text, reply_markup=builder.as_markup())


@router.callback_query(MyCallback.filter(F.foo == 'next'))
async def week_grade_n(callback: types.CallbackQuery, callback_data: MyCallback):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text="Поиск оценок...")

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)
    result = await AISdnevnik(log=log, passw=pasw).select_var(
        callback_data.value, page=callback_data.page)

    if isinstance(result, str):
        builder = InlineKeyboardBuilder()
        builder.button(text="Назад", callback_data='grades')
        builder.adjust(1)
        await callback.message.answer(text=result, reply_markup=builder.as_markup())

    elif isinstance(result, tuple):
        text = result[0]
        next_page = result[1]
        previous_page = result[2]
        page = result[3]

        if next_page is True:
            next_page = page + 1
        if previous_page is True:
            previous_page = page - 1

        builder = InlineKeyboardBuilder()

        if previous_page is False:
            builder.button(text='Конец', callback_data='end')
        else:
            builder.button(text='Предыдущая неделя', callback_data=MyCallback(foo='previous', value=callback_data.value, page=previous_page))
        if next_page is False:
            builder.button(text='Конец', callback_data='end')
        else:
            builder.button(text='Следующая неделя', callback_data=MyCallback(foo='next', value=callback_data.value, page=next_page))

        builder.button(text="Назад", callback_data='grades')
        builder.adjust(2)

        await callback.message.answer(text=text, reply_markup=builder.as_markup())


@router.callback_query(MyCallback.filter(F.foo == 'previous'))
async def week_grade_p(callback: types.CallbackQuery, callback_data: MyCallback):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text="Поиск оценок...")

    us_id = callback.from_user.id
    log, pasw = await get_default_credentials(us_id)
    result = await AISdnevnik(log=log, passw=pasw).select_var(
        callback_data.value, page=callback_data.page)

    if isinstance(result, str):
        builder = InlineKeyboardBuilder()
        builder.button(text="Назад", callback_data='grades')
        builder.adjust(1)
        await callback.message.answer(text=result, reply_markup=builder.as_markup())

    elif isinstance(result, tuple):
        text = result[0]
        next_page = result[1]
        previous_page = result[2]
        page = result[3]

        if next_page is True:
            next_page = page + 1
        if previous_page is True:
            previous_page = page - 1

        builder = InlineKeyboardBuilder()

        if previous_page is False:
            builder.button(text='Конец', callback_data='end')
        else:
            builder.button(text='Предыдущая неделя', callback_data=MyCallback(foo='previous', value=callback_data.value, page=previous_page))
        if next_page is False:
            builder.button(text='Конец', callback_data='end')
        else:
            builder.button(text='Следующая неделя', callback_data=MyCallback(foo='next', value=callback_data.value, page=next_page))

        builder.button(text="Назад", callback_data='grades')
        builder.adjust(2)

        await callback.message.answer(text=text, reply_markup=builder.as_markup())
