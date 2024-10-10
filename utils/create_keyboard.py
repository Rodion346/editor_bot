from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CreateKeyboard:
    def __init__(self):
        """Инициализация класса CreateKeyboard."""
        pass

    @staticmethod
    async def create_kb_menu():
        k_b = InlineKeyboardBuilder()
        btn_thematic_blocks = InlineKeyboardButton(
            text="Тематические блоки", callback_data="thematic_blocks"
        )
        btn_publication_schedule = InlineKeyboardButton(
            text="Расписание публикаций", callback_data="publication_schedule"
        )
        btn_administration = InlineKeyboardButton(
            text="Администрирование", callback_data="administration"
        )
        btn_rewrite = InlineKeyboardButton(text="Рерайт", callback_data="Rewrite")
        btn_statistics = InlineKeyboardButton(
            text="Статистика", callback_data="statistics"
        )
        btn_comments = InlineKeyboardButton(
            text="Комментарии", callback_data="comments"
        )
        k_b.row(btn_thematic_blocks)
        k_b.row(btn_publication_schedule)
        k_b.row(btn_administration)
        k_b.row(btn_rewrite)
        k_b.row(btn_statistics)
        k_b.row(btn_comments)

        return k_b.as_markup()

    @staticmethod
    async def create_keyboard(buttons, columns=1):
        keyboard_buttons = []
        for i in range(0, len(buttons), columns):
            row = [
                types.KeyboardButton(text=button) for button in buttons[i : i + columns]
            ]
            keyboard_buttons.append(row)
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=keyboard_buttons, resize_keyboard=True
        )
        return keyboard

    @staticmethod
    async def create_tb(names_tb, row=1):
        k_b = InlineKeyboardBuilder()
        for i in range(0, len(names_tb), row):
            row_buttons = [
                InlineKeyboardButton(
                    text=name.name,
                    callback_data=f"tb_{name.name}",
                )
                for name in names_tb[i : i + row]
            ]
            k_b.row(*row_buttons)

        k_b.row(InlineKeyboardButton(text="Создать блок", callback_data="create_block"))
        k_b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
        keyboard = k_b.as_markup()
        return keyboard

    @staticmethod
    async def create_tb_individual(name):
        kb = InlineKeyboardBuilder()
        btn_change_name = InlineKeyboardButton(
            text="Изменить название", callback_data=f"changetb_name_{name}"
        )
        btn_change_source = InlineKeyboardButton(
            text="Изменить источник", callback_data=f"changetb_source_{name}"
        )
        btn_change_description = InlineKeyboardButton(
            text="Изменить описание", callback_data=f"changetb_description_{name}"
        )
        btn_back = InlineKeyboardButton(text="Назад", callback_data="thematic_blocks")

        kb.row(btn_change_name)
        kb.row(btn_change_source)
        kb.row(btn_change_description)
        kb.row(btn_back)

        keyboard = kb.as_markup()
        return keyboard

    @staticmethod
    async def create_ps():
        kb = InlineKeyboardBuilder()
        btn_weekday = InlineKeyboardButton(
            text="Будний день", callback_data=f"ps_weekday"
        )
        btn_weekend = InlineKeyboardButton(text="Выходной", callback_data=f"ps_weekend")
        btn_event = InlineKeyboardButton(text="Событие", callback_data=f"ps_event")
        btn_back = InlineKeyboardButton(text="Назад", callback_data="back_to_main")

        kb.row(btn_weekday)
        kb.row(btn_weekend)
        kb.row(btn_event)
        kb.row(btn_back)

        keyboard = kb.as_markup()
        return keyboard

    @staticmethod
    async def create_ps_event():
        kb = InlineKeyboardBuilder()
        btn_list_events = InlineKeyboardButton(
            text="Список событий", callback_data=f"list_events"
        )
        btn_add_event = InlineKeyboardButton(
            text="Добавить событие", callback_data=f"add_event"
        )
        btn_back = InlineKeyboardButton(
            text="Назад", callback_data="publication_schedule"
        )

        kb.row(btn_list_events)
        kb.row(btn_add_event)
        kb.row(btn_back)

        keyboard = kb.as_markup()
        return keyboard


create_kb = CreateKeyboard()
