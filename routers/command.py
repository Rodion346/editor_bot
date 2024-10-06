from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from utils.create_keyboard import create_kb

command_router = Router()


@command_router.message(Command("start"))
async def process_start_command(message: types.Message):
    buttons = ["Меню"]
    start_txt = "Привет"
    await message.answer(
        start_txt, reply_markup=await create_kb.create_keyboard(buttons)
    )


@command_router.message(F.text == "Меню")
async def inline_menu(message: types.Message):
    await message.answer("Меню:", reply_markup=await create_kb.create_kb_menu())


@command_router.callback_query(F.data == "back_to_main")
async def back_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Menu", reply_markup=await create_kb.create_kb_menu()
    )
