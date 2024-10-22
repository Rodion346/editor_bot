from functools import wraps

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from core.repositories import ThematicBlockRepository
from core.repositories.admin import AdminRepository
from core.repositories.publication import PublicationRepository
from utils.adm import check_permission
from utils.create_keyboard import create_kb

publication_schedule_router = Router()
repo = PublicationRepository()
repo_block = ThematicBlockRepository()
repo_adm = AdminRepository()


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
@check_permission("event")
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    data = callback_query.data.split("_")
    list_pb = await repo.select_all()
    page = int(data[2]) if len(data) > 2 else 0
    page_size = 20

    if data[1] == "weekday":
        AddTime.today = 0
        filtered_pb = [pb for pb in list_pb if pb.today < 5]
    elif data[1] == "weekend":
        AddTime.today = 5
        filtered_pb = [pb for pb in list_pb if pb.today > 4]

    total_pages = (len(filtered_pb) + page_size - 1) // page_size
    start_idx = page * page_size
    end_idx = start_idx + page_size
    current_page_pb = filtered_pb[start_idx:end_idx]

    for pb in current_page_pb:
        block = await repo_block.select_id(str(pb.thematic_block_id).split(","))
        tx = ", ".join([i.name for i in block])
        btn = InlineKeyboardButton(
            text=f"{pb.time} || {tx}", callback_data=f"pb_{pb.id}"
        )
        kb.row(btn)

    if total_pages > 1:
        if page > 0:
            btn_prev = InlineKeyboardButton(
                text="<< Назад", callback_data=f"ps_{data[1]}_{page-1}"
            )
            kb.row(btn_prev)
        if page < total_pages - 1:
            btn_next = InlineKeyboardButton(
                text="Вперед >>", callback_data=f"ps_{data[1]}_{page+1}"
            )
            kb.row(btn_next)

    btn_add_time = InlineKeyboardButton(text="Добавить время", callback_data="add_time")
    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.row(btn_add_time)
    kb.row(btn_back)

    await callback_query.message.edit_text("Публикации:", reply_markup=kb.as_markup())
    await state.set_state(Pub.id)


@publication_schedule_router.callback_query(F.data.startswith("pb_"))
@check_permission("event")
async def publication_detail(callback_query: CallbackQuery, state: FSMContext):
    pb_id = callback_query.data.split("_")[1]
    pb = await repo.select_id(pb_id)
    block = await repo_block.select_id(pb.thematic_block_id)
    kb = InlineKeyboardBuilder()
    btn_edit_time = InlineKeyboardButton(
        text="Изменить время", callback_data=f"changepb_edit_time_{pb_id}"
    )
    btn_edit_tb = InlineKeyboardButton(
        text="Изменить блок", callback_data=f"changepb_edit_tb_{pb_id}"
    )
    btn_delete_tb = InlineKeyboardButton(
        text="Удалить", callback_data=f"changepb_delete_{pb_id}"
    )
    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.add(btn_edit_time)
    kb.add(btn_edit_tb)
    kb.add(btn_delete_tb)
    kb.add(btn_back)
    await callback_query.message.edit_text(
        f"{pb.time} || {block.name}\n", reply_markup=kb.as_markup()
    )
    await state.clear()


@publication_schedule_router.callback_query(F.data.startswith("changepb_"))
@check_permission("edit_time")
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    text = ""
    data = callback_query.data.split("_")
    if "delete" not in data:
        EditPb.column = data[2]
        EditPb.id = data[3]
    else:
        btn_back = InlineKeyboardButton(
            text="Назад", callback_data="publication_schedule"
        )
        kb.row(btn_back)
        await repo.delete(int(data[2]))
        await callback_query.message.answer("Удалено", reply_markup=kb.as_markup())
        await state.clear()
        return
    if "tb" in data:
        list_tb = await repo_block.select_all()
        for tb in list_tb:
            text += f"{tb.id} - {tb.name}\n"
    await callback_query.message.answer(text + "Введите новое значение")
    await state.set_state(EditPb.value)


@publication_schedule_router.message(EditPb.value)
@check_permission("edit_time")
async def publication_data(message: Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    print(EditPb.id)
    if EditPb.column == "tb":
        EditPb.column = "thematic_block_id"
    await repo.update(int(EditPb.id), EditPb.column, message.text)
    await state.clear()
    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.add(btn_back)
    await message.answer("Изменено", reply_markup=kb.as_markup())


@publication_schedule_router.callback_query(F.data.startswith("add_time"))
@check_permission("add_time")
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите время чч:мм")
    await state.set_state(AddTime.time)


@publication_schedule_router.message(AddTime.time)
@check_permission("add_time")
async def publication_data(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    list_pb = await repo_block.select_all()
    page = 0  # Начальная страница
    page_size = 20

    total_pages = (len(list_pb) + page_size - 1) // page_size
    start_idx = page * page_size
    end_idx = start_idx + page_size
    current_page_pb = list_pb[start_idx:end_idx]

    kb = InlineKeyboardBuilder()
    for pb in current_page_pb:
        btn = InlineKeyboardButton(
            text=f"{pb.name}", callback_data=f"select_block_{pb.id}"
        )
        kb.row(btn)

    if total_pages > 1:
        if page > 0:
            btn_prev = InlineKeyboardButton(
                text="<< Назад", callback_data=f"blocks_{page-1}"
            )
            kb.row(btn_prev)
        if page < total_pages - 1:
            btn_next = InlineKeyboardButton(
                text="Вперед >>", callback_data=f"blocks_{page+1}"
            )
            kb.row(btn_next)

    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.row(btn_back)

    await message.answer("Выберите блок(и):", reply_markup=kb.as_markup())
    await state.set_state(AddTime.tb)


@publication_schedule_router.callback_query(F.data.startswith("blocks_"))
@check_permission("add_time")
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    page = int(callback_query.data.split("_")[1])
    list_pb = await repo_block.select_all()
    page_size = 20

    total_pages = (len(list_pb) + page_size - 1) // page_size
    start_idx = page * page_size
    end_idx = start_idx + page_size
    current_page_pb = list_pb[start_idx:end_idx]

    kb = InlineKeyboardBuilder()
    for pb in current_page_pb:
        btn = InlineKeyboardButton(
            text=f"{pb.name}", callback_data=f"select_block_{pb.id}"
        )
        kb.row(btn)

    if total_pages > 1:
        if page > 0:
            btn_prev = InlineKeyboardButton(
                text="<< Назад", callback_data=f"blocks_{page-1}"
            )
            kb.row(btn_prev)
        if page < total_pages - 1:
            btn_next = InlineKeyboardButton(
                text="Вперед >>", callback_data=f"blocks_{page+1}"
            )
            kb.row(btn_next)

    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.row(btn_back)

    await callback_query.message.edit_text(
        "Выберите блок(и):", reply_markup=kb.as_markup()
    )
    await state.set_state(AddTime.tb)


@publication_schedule_router.callback_query(F.data.startswith("select_block_"))
@check_permission("add_time")
async def publication_data(callback_query: CallbackQuery, state: FSMContext):
    block_id = callback_query.data.split("_")[2]
    await state.update_data(tb=block_id)
    data = await state.get_data()
    await state.clear()
    await repo.add(data.get("time"), data.get("tb"), AddTime.today)

    kb = InlineKeyboardBuilder()
    btn_back = InlineKeyboardButton(text="Назад", callback_data="publication_schedule")
    kb.row(btn_back)

    await callback_query.message.edit_text(
        f"Вы установили ТБ {data.get('tb')} на {data.get('time')}",
        reply_markup=kb.as_markup(),
    )
