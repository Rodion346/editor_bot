from pkgutil import get_data

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import True_
from sqlalchemy.util import await_only

from utils.create_keyboard import create_kb
from core.repositories.admin import AdminRepository

repo = AdminRepository()
admin_router = Router()


class Admin(StatesGroup):
    id_adm = State()


@admin_router.callback_query(F.data == "administration")
async def admin_menu(callback_query: CallbackQuery):
    kb = InlineKeyboardBuilder()
    btn_list = InlineKeyboardButton(text="Список админов", callback_data="admin_list")
    btn_add_admin = InlineKeyboardButton(
        text="Добавить админа", callback_data="admin_add"
    )
    btn_back = InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    kb.row(btn_list)
    kb.row(btn_add_admin)
    kb.row(btn_back)
    await callback_query.message.edit_text("ADMINS", reply_markup=kb.as_markup())


@admin_router.callback_query(F.data == "admin_list")
async def admin_list(callback_query: CallbackQuery):
    adm_list = await repo.select_all()
    await callback_query.message.edit_text(
        "Выберите админа:", reply_markup=await create_kb.create_adm_list(adm_list)
    )


@admin_router.callback_query(F.data == "admin_add")
async def admin_add_id(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите id:")
    await state.set_state(Admin.id_adm)


@admin_router.message(Admin.id_adm)
async def admin_add_status(message: Message, state: FSMContext):
    await state.update_data(id_adm=message.text)
    data = await state.get_data()
    await repo.add(data.get("id_adm"))
    adm = await repo.select_adm_id(data.get("id_adm"))
    await message.answer(
        f"Админ с id {data.get('id_adm')} успешно создан\nНастройте права:",
        reply_markup=await create_kb.create_rights(adm),
    )
    await state.clear()


@admin_router.callback_query(F.data.startswith("ad_"))
async def admin(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="Показать права", callback_data=f"show_rights_{data[1]}"
        )
    )
    kb.row(
        InlineKeyboardButton(
            text="Удалить", callback_data=f"delete_admin_check_{data[1]}"
        )
    )
    kb.row(InlineKeyboardButton(text="Назад", callback_data="admin_list"))

    await callback_query.message.edit_text(f"id {data[1]}", reply_markup=kb.as_markup())


@admin_router.callback_query(F.data.startswith("show_rights_"))
async def rights(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    adm = await repo.select_adm_id(data[2])
    await callback_query.message.edit_reply_markup(
        reply_markup=await create_kb.create_rights(adm)
    )


@admin_router.callback_query(F.data.startswith("show_redact_"))
async def rights(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    if data[2].lower() == "true":
        original_value = True
    elif data[2].lower() == "false":
        original_value = False
    await repo.update(
        adm_id=int(data[3]),
        column=data[4] + ("_" + data[5] if len(data) == 6 else ""),
        new_value=not original_value,
    )
    adm = await repo.select_adm_id(data[3])
    await callback_query.message.edit_reply_markup(
        reply_markup=await create_kb.create_rights(adm)
    )


@admin_router.callback_query(F.data.startswith("delete_admin_check_"))
async def delete_admin_check(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Да", callback_data=f"delete_admin_{data[3]}"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data=f"admin_list"))
    await callback_query.message.edit_text(
        "Выберите админа:", reply_markup=kb.as_markup()
    )


@admin_router.callback_query(F.data.startswith("delete_admin_"))
async def delete_admin(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    adm = await repo.delete(int(data[2]))
    adm_list = await repo.select_all()
    await callback_query.message.edit_text(
        "Выберите админа:", reply_markup=await create_kb.create_adm_list(adm_list)
    )
