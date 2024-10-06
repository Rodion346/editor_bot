from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.create_keyboard import create_kb

publication_schedule_router = Router()


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
