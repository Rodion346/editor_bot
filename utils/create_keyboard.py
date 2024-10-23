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
        btn_change_backtime = InlineKeyboardButton(
            text="Изменить время поиска", callback_data=f"changetb_timeback_{name}"
        )
        btn_back = InlineKeyboardButton(text="Назад", callback_data="thematic_blocks")

        kb.row(btn_change_name)
        kb.row(btn_change_source)
        kb.row(btn_change_description)
        kb.row(btn_change_backtime)
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
        btn_event = InlineKeyboardButton(text="Событие", callback_data=f"event")
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

    @staticmethod
    async def create_adm_list(adm_list):
        k_b = InlineKeyboardBuilder()
        for i in range(0, len(adm_list), 1):
            row_buttons = [
                InlineKeyboardButton(
                    text=f"id {adm.admin_id}",
                    callback_data=f"ad_{adm.admin_id}",
                )
                for adm in adm_list[i : i + 1]
            ]
            k_b.row(*row_buttons)

        k_b.row(InlineKeyboardButton(text="Назад", callback_data="administration"))
        keyboard = k_b.as_markup()
        return keyboard

    @staticmethod
    async def create_rights(adm):
        kb = InlineKeyboardBuilder()
        kb.row(
            InlineKeyboardButton(
                text=f"Добавить ТБ || {'Есть' if adm.add_tb is True else 'Нет'}",
                callback_data=f"show_redact_{adm.add_tb}_{adm.admin_id}_add_tb",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Редактировать ТБ || {'Есть' if adm.edit_tb is True else 'Нет'}",
                callback_data=f"show_redact_{adm.edit_tb}_{adm.admin_id}_add_tb",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Удалить ТБ || {'Есть' if adm.del_tb is True else 'Нет'}",
                callback_data=f"show_redact_{adm.del_tb}_{adm.admin_id}_del_tb",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Добавить время || {'Есть' if adm.add_time is True else 'Нет'}",
                callback_data=f"show_redact_{adm.add_time}_{adm.admin_id}_add_time",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Редактировать время || {'Есть' if adm.edit_time is True else 'Нет'}",
                callback_data=f"show_redact_{adm.edit_time}_{adm.admin_id}_edit_time",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Удалить время || {'Есть' if adm.del_time is True else 'Нет'}",
                callback_data=f"show_redact_{adm.del_time}_{adm.admin_id}_del_time",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Добавить источники || {'Есть' if adm.add_source is True else 'Нет'}",
                callback_data=f"show_redact_{adm.add_source}_{adm.admin_id}_add_source",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Редактировать источники || {'Есть' if adm.edit_source is True else 'Нет'}",
                callback_data=f"show_redact_{adm.edit_source}_{adm.admin_id}_edit_source",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Удалить источники || {'Есть' if adm.del_source is True else 'Нет'}",
                callback_data=f"show_redact_{adm.del_source}_{adm.admin_id}_del_source",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Рерайт || {'Есть' if adm.rerate is True else 'Нет'}",
                callback_data=f"show_redact_{adm.rerate}_{adm.admin_id}_rerate",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"Комментарии || {'Есть' if adm.comments is True else 'Нет'}",
                callback_data=f"show_redact_{adm.comments}_{adm.admin_id}_comments",
            )
        )
        kb.row(
            InlineKeyboardButton(
                text=f"События || {'Есть' if adm.event is True else 'Нет'}",
                callback_data=f"show_redact_{adm.event}_{adm.admin_id}_event",
            )
        )
        kb.row(InlineKeyboardButton(text="Назад", callback_data="admin_list"))

        return kb.as_markup()

    @staticmethod
    async def create_ev_individual(name):
        kb = InlineKeyboardBuilder()
        btn_change_name = InlineKeyboardButton(
            text="Изменить название", callback_data=f"evchange_name_{name}"
        )
        btn_change_source = InlineKeyboardButton(
            text="Изменить источник", callback_data=f"evchange_source_{name}"
        )
        btn_change_description = InlineKeyboardButton(
            text="Изменить описание", callback_data=f"evchange_description_{name}"
        )
        btn_change_timein = InlineKeyboardButton(
            text="Изменить время входа", callback_data=f"evchange_time_in_{name}"
        )
        btn_change_timeout = InlineKeyboardButton(
            text="Изменить время выхода", callback_data=f"evchange_time_out_{name}"
        )
        btn_back = InlineKeyboardButton(text="Назад", callback_data="list_events")

        kb.row(btn_change_name)
        kb.row(btn_change_source)
        kb.row(btn_change_description)
        kb.row(btn_change_timein)
        kb.row(btn_change_timeout)
        kb.row(btn_back)

        keyboard = kb.as_markup()
        return keyboard


create_kb = CreateKeyboard()
