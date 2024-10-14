from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from core.repositories import ThematicBlockRepository
from core.repositories.event import EventRepository
from utils.create_keyboard import create_kb

event_router = Router()
repo = EventRepository()


class Event(StatesGroup):
    event = State()


class Change_ev(StatesGroup):
    model: str
    value = State()
    mess_id: int


class CreateEvent(StatesGroup):
    name = State()
    source = State()
    description = State()
    time_in = State()
    time_out = State()


@event_router.callback_query(F.data == "event")
async def event_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "События:", reply_markup=await create_kb.create_ps_event()
    )


@event_router.callback_query(F.data == "list_events")
async def event_list(callback_query: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Назад", callback_data="event"))
    event_list = await repo.select_all()
    form_text = ""
    for event in event_list:
        form_text += (
            f"{event.id} - с {event.time_in} по {event.time_out} || {event.name}\n"
        )
    await callback_query.message.edit_text(
        "Выберите событие:\n" + form_text, reply_markup=kb.as_markup()
    )
    await state.set_state(Event.event)


@event_router.message(Event.event)
async def event(message: Message, state: FSMContext):
    event = await repo.select_id(message.text)
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text="Удалить", callback_data="delete_event"),
        InlineKeyboardButton(text="Изменить", callback_data=f"edit_event_{event.name}"),
    )
    await message.answer(
        f"С {event.time_in} по {event.time_out} || {event.name}\n",
        reply_markup=kb.as_markup(),
    )
    await state.clear()


@event_router.callback_query(F.data == "add_event")
async def create_block(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название")
    await state.set_state(CreateEvent.name)


@event_router.message(CreateEvent.name)
async def source_block(message: Message, state: FSMContext):
    await message.answer("Введите источник")
    await state.update_data(name=message.text)
    await state.set_state(CreateEvent.source)


@event_router.message(CreateEvent.source)
async def description_block(message: Message, state: FSMContext):
    await message.answer("Введите описание")
    await state.update_data(source=message.text)
    await state.set_state(CreateEvent.description)


@event_router.message(CreateEvent.description)
async def description_block(message: Message, state: FSMContext):
    await message.answer("Введите первую точку времени")
    await state.update_data(description=message.text)
    await state.set_state(CreateEvent.time_in)


@event_router.message(CreateEvent.time_in)
async def description_block(message: Message, state: FSMContext):
    await message.answer("Введите вторую точку времени")
    await state.update_data(time_in=message.text)
    await state.set_state(CreateEvent.time_out)


@event_router.message(CreateEvent.time_out)
async def description_block(message: Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Назад", callback_data="list_events"))
    await state.update_data(time_out=message.text)
    data = await state.get_data()
    await repo.add(
        data.get("name"),
        data.get("source"),
        data.get("description"),
        data.get("time_in"),
        data.get("time_out"),
    )
    await message.answer(
        f"Событие: {data.get('name')}\nУспешно создано", reply_markup=kb.as_markup()
    )
    await state.clear()


@event_router.callback_query(F.data.startswith("edit_event"))
async def change_mess(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    print(data)
    await callback_query.message.edit_reply_markup(
        reply_markup=await create_kb.create_ev_individual(data[2])
    )


@event_router.callback_query(F.data.startswith("evchange_"))
async def create_change_mess_ev(callback_query: CallbackQuery, state: FSMContext):
    change = callback_query.data.split("_")
    Change_ev.model = change
    Change_ev.mess_id = callback_query.message.business_connection_id
    await callback_query.message.answer("Введите новое значение")
    await state.set_state(Change_ev.value)


@event_router.message(Change_ev.value)
async def description_block(message: Message, state: FSMContext):
    await state.update_data(value=message.text)
    data = await state.get_data()
    model = Change_ev.model
    print(model)
    q = await repo.update(
        model[2] if len(model) < 4 else model[3],
        model[1] + ("_" + model[2] if len(model) == 4 else ""),
        data.get("value"),
    )
    await message.answer("OK")
    await state.clear()
