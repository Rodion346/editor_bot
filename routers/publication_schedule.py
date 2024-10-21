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


class EditPb(StatesGroup):
    id: str
    value = State()
    column: str


class Pub(StatesGroup):
    id = State()


@publication_schedule_router.callback_query(F.data == "publication_schedule")
async def publication_schedule_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Расписание публикаций", reply_markup=await create_kb.create_ps()
    )


@publication_schedule_router.callback_query(F.data.startswith("ps_"))
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    text = "Публикации:\n"
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
                    block = await repo_block.select_id(
                        str(pb.thematic_block_id).split(",")
                    )
                    tx = ""
                    for i in block:
                        tx += i.name
                        tx += ","
                    text += f"{pb.id} - {pb.time} || {tx.rstrip(',')}\n"

    elif data[1] == "weekend":
        AddTime.today = 5
        if list_pb:
            for pb in list_pb:
                if pb.today > 4:
                    block = await repo_block.select_id(
                        str(pb.thematic_block_id).split(",")
                    )
                    tx = ""
                    for i in block:
                        tx += i.name
                        tx += ","
                    text += f"{pb.id} - {pb.time} || {tx.rstrip(',')}\n"

    await callback_query.message.edit_text(
        text + "выберите номер", reply_markup=kb.as_markup()
    )
    await state.set_state(Pub.id)


@publication_schedule_router.message(Pub.id)
async def publication_data(message: Message, state: FSMContext):
    pb = await repo.select_id(message.text)
    block = await repo_block.select_id(pb.thematic_block_id)
    kb = InlineKeyboardBuilder()
    btn_edit_time = InlineKeyboardButton(
        text="Изменить время", callback_data=f"changepb_edit_time_{message.text}"
    )
    btn_edit_tb = InlineKeyboardButton(
        text="Изменить блок", callback_data=f"changepb_edit_tb_{message.text}"
    )
    btn_delete_tb = InlineKeyboardButton(
        text="Удалить", callback_data=f"changepb_delete_{message.text}"
    )
    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.add(btn_edit_time)
    kb.add(btn_edit_tb)
    kb.add(btn_delete_tb)
    kb.add(btn_back)
    await message.answer(
        f"{pb.id} - {pb.time} || {block.name}\n", reply_markup=kb.as_markup()
    )
    await state.clear()


@publication_schedule_router.callback_query(F.data.startswith("changepb_"))
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    text = ""
    data = callback_query.data.split("_")
    if "delete" not in data:
        EditPb.column = data[2]
        EditPb.id = data[3]
    else:
        await repo.delete(int(data[2]))
        await callback_query.message.answer("Удалено")
    if "tb" in data:
        list_tb = await repo_block.select_all()
        for tb in list_tb:
            text += f"{tb.id} - {tb.name}\n"
    await callback_query.message.answer(text + "Введите новое значение")
    await state.set_state(EditPb.value)


@publication_schedule_router.message(EditPb.value)
async def publication_data(message: Message, state: FSMContext):
    print(EditPb.id)
    if EditPb.column == "tb":
        EditPb.column = "thematic_block_id"
    await repo.update(int(EditPb.id), EditPb.column, message.text)
    await state.clear()
    await message.answer("Изменено")


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

    await message.answer(tb_text + "\nВыберите номер(a) блока(ов):")
    await state.set_state(AddTime.tb)


@publication_schedule_router.message(AddTime.tb)
async def publication_data(message: Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Назад", callback_data="publication_schedule"))
    await state.update_data(tb=message.text)
    data = await state.get_data()
    await state.clear()
    await repo.add(data.get("time"), data.get("tb"), AddTime.today)
    await message.answer(
        f"Вы установили ТБ {data.get('tb')} на {data.get('time')}",
        reply_markup=kb.as_markup(),
    )
