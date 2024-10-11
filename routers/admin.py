from pkgutil import get_data

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp.web_middlewares import middleware
from tomlkit import value

admin_router = Router()


@admin_router.callback_query(F.data == "administration")
async def admin_menu(callback_query: CallbackQuery):
    kb = InlineKeyboardBuilder()
    btn_list = InlineKeyboardButton(text="Список админов", callback_data="admin_list")
    btn_back = InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    kb.row(btn_list)
    kb.row(btn_back)
    await callback_query.message.edit_text("ADMINS", reply_markup=kb.as_markup())
