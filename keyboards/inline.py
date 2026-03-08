from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="☁️ TimeWeb", callback_data="menu_timeweb"),
            InlineKeyboardButton(text="🤖 PolzaAI", callback_data="menu_polzaai"),
        ],
        [
            InlineKeyboardButton(text="🔍 Яндекс Вебмастер", callback_data="menu_yandex"),
        ],
        [
            InlineKeyboardButton(text="📊 Полный отчёт", callback_data="full_report"),
        ],
    ])


def timeweb_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="tw_balance"),
            InlineKeyboardButton(text="🖥️ Серверы", callback_data="tw_servers"),
        ],
        [
            InlineKeyboardButton(text="🌐 Домены", callback_data="tw_domains"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"),
        ],
    ])


def yandex_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Индексация", callback_data="yx_indexing"),
            InlineKeyboardButton(text="🔎 Запросы", callback_data="yx_queries"),
        ],
        [
            InlineKeyboardButton(text="⚠️ Ошибки", callback_data="yx_errors"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"),
        ],
    ])


def servers_menu(servers: list) -> InlineKeyboardMarkup:
    buttons = []
    for s in servers:
        status_icon = "🟢" if s["status"] == "on" else "🔴"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} {s['name']}",
                callback_data=f"server_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu_timeweb")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def server_actions_menu(server_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="♻️ Мягкая перезагрузка", callback_data=f"soft_reboot_{server_id}"),
        ],
        [
            InlineKeyboardButton(text="🔄 Жёсткая перезагрузка", callback_data=f"reboot_{server_id}"),
        ],
        [
            InlineKeyboardButton(text="🟢 Включить", callback_data=f"start_{server_id}"),
            InlineKeyboardButton(text="🔴 Выключить", callback_data=f"stop_{server_id}"),
        ],
        [
            InlineKeyboardButton(text="◀️ К серверам", callback_data="tw_servers"),
        ],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
