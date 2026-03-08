from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="вЃпёЏ TimeWeb", callback_data="menu_timeweb"),
            InlineKeyboardButton(text="рџ¤– PolzaAI", callback_data="menu_polzaai"),
        ],
        [
            InlineKeyboardButton(text="рџ”Ќ РЇРЅРґРµРєСЃ Р’РµР±РјР°СЃС‚РµСЂ", callback_data="menu_yandex"),
        ],
        [
            InlineKeyboardButton(text="рџ“Љ РџРѕР»РЅС‹Р№ РѕС‚С‡С‘С‚", callback_data="full_report"),
        ],
    ])


def timeweb_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="рџ’° Р‘Р°Р»Р°РЅСЃ", callback_data="tw_balance"),
            InlineKeyboardButton(text="рџ–ҐпёЏ РЎРµСЂРІРµСЂС‹", callback_data="tw_servers"),
        ],
        [
            InlineKeyboardButton(text="рџЊђ Р”РѕРјРµРЅС‹", callback_data="tw_domains"),
        ],
        [
            InlineKeyboardButton(text="в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="main_menu"),
        ],
    ])


def yandex_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="рџ“€ РРЅРґРµРєСЃР°С†РёСЏ", callback_data="yx_indexing"),
            InlineKeyboardButton(text="рџ”Ћ Р—Р°РїСЂРѕСЃС‹", callback_data="yx_queries"),
        ],
        [
            InlineKeyboardButton(text="вљ пёЏ РћС€РёР±РєРё", callback_data="yx_errors"),
        ],
        [
            InlineKeyboardButton(text="в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="main_menu"),
        ],
    ])


def servers_menu(servers: list) -> InlineKeyboardMarkup:
    buttons = []
    for s in servers:
        status_icon = "рџџў" if s["status"] == "on" else "рџ”ґ"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} {s['name']}",
                callback_data=f"server_{s['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="menu_timeweb")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def server_actions_menu(server_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="рџ”„ РџРµСЂРµР·Р°РіСЂСѓР·РёС‚СЊ", callback_data=f"reboot_{server_id}"),
        ],
        [
            InlineKeyboardButton(text="в—ЂпёЏ Рљ СЃРµСЂРІРµСЂР°Рј", callback_data="tw_servers"),
        ],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="в—ЂпёЏ Р“Р»Р°РІРЅРѕРµ РјРµРЅСЋ", callback_data="main_menu")]
    ])
