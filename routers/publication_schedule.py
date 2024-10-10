from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from core.repositories import ThematicBlockRepository
from core.repositories.publication import PublicationRepository
from utils.create_keyboard import create_kb

publication_schedule_router = Router()
repo = PublicationRepository()
repo_block = ThematicBlockRepository()


class AddTime(StatesGroup):
    time = State()
    tb = State()
    today: int


@publication_schedule_router.callback_query(F.data == "publication_schedule")
async def publication_schedule_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Расписание публикаций", reply_markup=await create_kb.create_ps()
    )


@publication_schedule_router.callback_query(F.data == "event")
async def event_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "События:", reply_markup=await create_kb.create_ps_event()
    )


@publication_schedule_router.callback_query(F.data.startswith("ps_"))
async def publication_data(callback_query: CallbackQuery):
    kb = InlineKeyboardBuilder()
    text = "Тест\n"
    btn_add_time = InlineKeyboardButton(text="Добавить время", callback_data="add_time")
    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.row(btn_add_time)
    kb.row(btn_back)
    data = callback_query.data.split("_")
    list_pb = await repo.select_all()
    if data[1] == "weekday":
        AddTime.today = 0
        if list_pb:
            for pb in list_pb:
                if pb.today < 5:
                    block = await repo_block.select_id(pb.thematic_block_id)
                    text += f"{pb.id} - {pb.time} || {block.name}\n"

    elif data[1] == "weekend":
        AddTime.today = 5
        if list_pb:
            for pb in list_pb:
                if pb.today > 4:
                    block = await repo_block.select_id(pb.thematic_block_id)
                    text += f"{pb.id} - {pb.time} || {block.name}\n"

    await callback_query.message.edit_text(text, reply_markup=kb.as_markup())


@publication_schedule_router.callback_query(F.data.startswith("add_time"))
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите время чч:мм")
    await state.set_state(AddTime.time)


@publication_schedule_router.message(AddTime.time)
async def publication_data(message: Message, state: FSMContext):
    tb_text = ""
    await state.update_data(time=message.text)
    list_pb = await repo_block.select_all()
    if list_pb:
        for pb in list_pb:
            block = await repo_block.select_id(pb.id)
            tb_text += f"{pb.id} - {block.name}\n"

    await message.answer(tb_text + "\nВыберите номер блока:")
    await state.set_state(AddTime.tb)


@publication_schedule_router.message(AddTime.tb)
async def publication_data(message: Message, state: FSMContext):
    await state.update_data(tb=message.text)
    data = await state.get_data()
    await state.clear()
    await repo.add(data.get("time"), data.get("tb"), AddTime.today)
    await message.answer("OK")
