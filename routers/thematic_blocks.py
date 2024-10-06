from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.create_keyboard import create_kb

thematic_blocks_router = Router()

list_tb = ["FGC", "DBS", "LSR"]


@thematic_blocks_router.callback_query(F.data == "thematic_blocks")
async def thematic_blocks_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "TB:", reply_markup=await create_kb.create_tb(list_tb)
    )


@thematic_blocks_router.callback_query(F.data.startswith("tb_"))
async def thematic_block(callback_query: CallbackQuery):
    form_text = ""
    name_tb = callback_query.data.split("_")
    name_tb = name_tb[1]
    form_text += name_tb + "\n"
    form_text += "Источники: 1, 2, 3\n"
    form_text += "Описание: DFsefkfskmdfm"

    await callback_query.message.edit_text(
        form_text, reply_markup=await create_kb.create_tb_individual(name_tb)
    )
