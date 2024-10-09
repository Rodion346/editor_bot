from pkgutil import get_data

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp.web_middlewares import middleware
from tomlkit import value

from utils.create_keyboard import create_kb
from core.repositories.thematic_block import ThematicBlockRepository

thematic_blocks_router = Router()
repo = ThematicBlockRepository()


class CreateBlock(StatesGroup):
    name = State()
    source = State()
    description = State()


class Change(StatesGroup):
    model: str
    value = State()
    mess_id: int


@thematic_blocks_router.callback_query(F.data == "thematic_blocks")
async def thematic_blocks_menu(callback_query: CallbackQuery):
    list_tb = await repo.select_all()
    await callback_query.message.edit_text(
        "TB:", reply_markup=await create_kb.create_tb(list_tb)
    )


@thematic_blocks_router.callback_query(F.data.startswith("tb_"))
async def thematic_block(callback_query: CallbackQuery):
    form_text = ""
    name_tb = callback_query.data.split("_")
    name_tb = name_tb[1]
    name_tb = await repo.select_name(name_tb)
    form_text += name_tb.name + "\n"
    form_text += f"Источники: {name_tb.source}\n"
    form_text += f"Описание: {name_tb.description}"

    await callback_query.message.edit_text(
        form_text, reply_markup=await create_kb.create_tb_individual(name_tb.name)
    )


@thematic_blocks_router.callback_query(F.data == "create_block")
async def create_block(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название")
    await state.set_state(CreateBlock.name)


@thematic_blocks_router.message(CreateBlock.name)
async def source_block(message: Message, state: FSMContext):
    await message.answer("Введите источник")
    await state.update_data(name=message.text)
    await state.set_state(CreateBlock.source)


@thematic_blocks_router.message(CreateBlock.source)
async def description_block(message: Message, state: FSMContext):
    await message.answer("Введите описание")
    await state.update_data(source=message.text)
    await state.set_state(CreateBlock.description)


@thematic_blocks_router.message(CreateBlock.description)
async def description_block(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await repo.add(data.get("name"), data.get("source"), data.get("description"))
    await message.answer(f"ТБ: {data.get('name')}\nУспешно создан")
    await state.clear()


@thematic_blocks_router.callback_query(F.data.startswith("changetb"))
async def create_change_mess(callback_query: CallbackQuery, state: FSMContext):
    change = callback_query.data.split("_")
    Change.model = change
    Change.mess_id = callback_query.message.business_connection_id
    await callback_query.message.answer("Введите новое значение")
    await state.set_state(Change.value)


@thematic_blocks_router.message(Change.value)
async def description_block(message: Message, state: FSMContext):
    await state.update_data(value=message.text)
    data = await state.get_data()
    model = Change.model
    print(model)
    q = await repo.update(model[2], model[1], data.get("value"))
    await message.answer("OK")
    await state.clear()
