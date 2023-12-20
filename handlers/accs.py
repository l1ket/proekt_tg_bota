# import sqlite3
from aiogram import F, Router
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from pars2 import ais_dnevnik
from .all_func import check_stasus, add_to_table, check_accs, check_login,  \
    get_all_accs, check_acc_in_bd


router = Router()
bot = Bot(token='6028764195:AAF1iMb6Vh_yYdJGnQsn73I3J1Vv4W-YoZc')
datas = []
ais = ais_dnevnik()


class get_data(StatesGroup):
    callback_check = State()
    get_name_acc = State()
    get_log = State()
    get_password = State()


@router.callback_query(F.data == 'add_ac')
async def skip(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(text='Проверка акаунта...')
    users_id = callback.from_user.id
    accounts = await check_accs(users_id)

    if accounts < 5:
        if accounts == 0:
            await state.update_data(new=True)
        else:
            await state.update_data(new=False)
        await callback.message.answer(
            text='Проверка пройдена, '
            'для проодолжения введите любое слово.')
        await state.set_state(get_data.callback_check)

    else:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(
            text='Количество ваших аккаунтов превысило 5 шт.\n'
            'Удалите ненужные аккаунты и начните процедуру заново.'
                                )

        builder = InlineKeyboardBuilder()
        builder.button(text="Главное меню", callback_data='start_back')
        builder.adjust(1)

        await callback.message.answer(
            text="Я не понял, нажмите кнопку ниже",
            reply_markup=builder.as_markup()
        )


@router.message(get_data.callback_check)
async def taking_name(message: Message, state: FSMContext):
    await message.answer(
        text="Введите название аккаунта.\n"
        "(чтобы отменить введите /cancel или напишите отмена)"
        )
    await state.set_state(get_data.get_name_acc)


@router.message(get_data.get_name_acc)
async def taking_log(message: Message, state: FSMContext):
    mes = message.text
    us_id = message.from_user.id
    if await check_login(message=mes, user_id=us_id) is True:
        await state.update_data(chosen_name=message.text)
        await message.answer(
            text="Спасибо.\nТеперь введите данные от аккаунта, "
            "сначала логин.",
            )
        await state.set_state(get_data.get_log)
    else:
        await message.answer(text='Такое имя уже занято.\n'
                             'Введте любое слово чтобы продолжить.')
        await state.set_state(get_data.callback_check)


@router.message(get_data.get_log)
async def taking_pass(message: Message, state: FSMContext):
    await state.update_data(chosen_log=message.text)
    await message.answer(
        text="Теперь пароль.",
        )
    await state.set_state(get_data.get_password)


@router.message(get_data.get_password)
async def acc_get(message: Message, state: FSMContext):

    builder = InlineKeyboardBuilder()
    builder.button(text="Главное меню", callback_data='start_back')
    builder.adjust(2)

    await state.update_data(chosen_pass=message.text)
    user_data = await state.get_data()
    status = await check_stasus(
        user_data['chosen_log'], user_data['chosen_pass']
        )

    if status == 200:
        users_id = message.from_user.id

        await message.answer(
            text=f"Данные сохранены.\n"
            f"Название аккаунта: {user_data['chosen_name']},\n"
            f"Ваш логин: {user_data['chosen_log']},\n"
            f"Ваш пароль: {user_data['chosen_pass']}.",
            reply_markup=builder.as_markup()
        )
        await add_to_table(
            users_id,
            user_data['chosen_name'],
            user_data['chosen_log'],
            user_data['chosen_pass'],
            is_used=user_data['new']
            )
        # Сброс состояния и сохранённых данных у пользователя
        await state.clear()

    else:
        await message.answer(text='Данные не подошли, введите их еще раз.'
                             '\nНачнем с логина:')
        await state.set_state(get_data.get_log)


"""
конец машины состояний
"""


@router.callback_query(F.data == 'check_acs')
async def check_acs(callback: types.CallbackQuery):
    await callback.answer(text='Проверка акаунта...')
    users_id = callback.from_user.id
    accounts = await get_all_accs(users_id)
    await callback.message.answer(text=accounts)

    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data='accs')
    builder.adjust(1)

    await callback.message.answer(
        text="Нажмите чтобы вернуться:", reply_markup=builder.as_markup()
        )


class del_account(StatesGroup):
    callback_check = State()


@router.callback_query(F.data == 'del_ac')
async def del_accs_check(callback: types.CallbackQuery, state: FSMContext):

    await callback.answer()
    users_id = callback.from_user.id
    accounts = await get_all_accs(users_id)
    # await callback.message.answer(text=accounts)

    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data='accs')
    builder.adjust(1)

    await callback.message.answer(text=accounts)
    await callback.message.answer(
        text='Введите название аккаунта',
        reply_markup=builder.as_markup()
                                  )
    await state.set_state(del_account.callback_check)


@router.message(del_account.callback_check)
async def del_accs(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data='YES')
    builder.button(text="Нет", callback_data='accs')
    builder.adjust(1)

    await message.answer(
        text="Вы уверены?", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == 'YES')
async def deliting_accs(callback: types.CallbackQuery, state: FSMContext):

    await callback.answer(text='Удаляем данные')
    us_id = callback.from_user.id
    name = await state.get_data()

    await check_acc_in_bd(
        user_id=str(us_id),
        acc_name=name['name']
        )
    await callback.answer(text='Успешно')
    await callback.message.delete()

    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data='start_back')
    builder.adjust(1)

    accounts = await get_all_accs(us_id)
    await callback.message.answer(text=accounts,
                                  reply_markup=builder.as_markup())
    await state.clear()
