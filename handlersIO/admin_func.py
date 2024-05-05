from aiogram import F, Router, Bot

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlersIO.getting_log_and_pass import return_user_ids
from dannie import TOKEN, ADMINS

router = Router()
bot = Bot(token=TOKEN)


class admins_states(StatesGroup):
    choose = State()
    mes = State()


@router.message(Command(commands='admin'))
async def message_from_admin(message: Message):
    if message.from_user.id in ADMINS:
        builder = InlineKeyboardBuilder()
        builder.button(text="Разослать всем сообщение",
                       callback_data='message_for_all')
        builder.button(text="Отмена", callback_data='cancel')
        builder.adjust(1)
        await message.answer(text='Привет, админ.',
                             reply_markup=builder.as_markup())
    else:
        await message.answer(text='В доступе отказано')


@router.callback_query(F.data == "message_for_all")
async def choose_message(callback: CallbackQuery,
                         state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        text="Введите сообщение для всех",
        )
    await state.set_state(admins_states.choose)


@router.message(admins_states.choose)
async def send_messages(message: Message, state: FSMContext):
    ids = await return_user_ids()
    for us_id in ids:
        us_id = int(us_id)
        await bot.send_message(chat_id=us_id,
                               text=message.text)
    await message.answer(
        text="Сообщение отправленно",
        )
    await state.clear()
