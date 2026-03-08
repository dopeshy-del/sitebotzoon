import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import api.timeweb as tw
import api.polzaai as polza
import api.yandex_webmaster as yx
import keyboards.inline as kb
import formatters as fmt

router = Router()


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ /start в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(
        "рџ‘‹ <b>Myzoon Monitor Bot</b>\n\n"
        "РњРѕРЅРёС‚РѕСЂРёРЅРі Рё СѓРїСЂР°РІР»РµРЅРёРµ РІР°С€РµР№ РёРЅС„СЂР°СЃС‚СЂСѓРєС‚СѓСЂРѕР№.\n"
        "Р’С‹Р±РµСЂРёС‚Рµ СЂР°Р·РґРµР»:",
        reply_markup=kb.main_menu(),
        parse_mode="HTML"
    )


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ /status в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.message(Command("status"))
async def cmd_status(msg: Message):
    wait = await msg.answer("вЏі РЎРѕР±РёСЂР°СЋ РґР°РЅРЅС‹Рµ...")
    servers = await tw.get_servers()
    text = fmt.fmt_servers_list(servers)
    await wait.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ /balance в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.message(Command("balance"))
async def cmd_balance(msg: Message):
    wait = await msg.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ Р±Р°Р»Р°РЅСЃС‹...")
    tw_bal, polzaai_bal = await asyncio.gather(
        tw.get_account_balance(),
        polza.get_balance()
    )
    text = fmt.fmt_timeweb_balance(tw_bal) + "\n\n" + fmt.fmt_polzaai_balance(polzaai_bal)
    await wait.edit_text(text, reply_markup=kb.back_to_main(), parse_mode="HTML")


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ /report в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.message(Command("report"))
async def cmd_report(msg: Message):
    await send_full_report(msg.chat.id, msg.bot)


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ Callback: РіР»Р°РІРЅРѕРµ РјРµРЅСЋ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(cb: CallbackQuery):
    await cb.message.edit_text(
        "рџ‘‹ <b>Myzoon Monitor Bot</b>\n\nР’С‹Р±РµСЂРёС‚Рµ СЂР°Р·РґРµР»:",
        reply_markup=kb.main_menu(),
        parse_mode="HTML"
    )
    await cb.answer()


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ Callback: TimeWeb в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.callback_query(F.data == "menu_timeweb")
async def cb_menu_timeweb(cb: CallbackQuery):
    await cb.message.edit_text(
        "вЃпёЏ <b>TimeWeb Cloud</b>\n\nР’С‹Р±РµСЂРёС‚Рµ СЂР°Р·РґРµР»:",
        reply_markup=kb.timeweb_menu(),
        parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "tw_balance")
async def cb_tw_balance(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    data = await tw.get_account_balance()
    await cb.message.edit_text(
        fmt.fmt_timeweb_balance(data),
        reply_markup=kb.timeweb_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tw_servers")
async def cb_tw_servers(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    servers = await tw.get_servers()
    await cb.message.edit_text(
        fmt.fmt_servers_list(servers),
        reply_markup=kb.servers_menu(servers),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("server_"))
async def cb_server_detail(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[1])
    await cb.answer("вЏі")
    servers = await tw.get_servers()
    server = next((s for s in servers if s["id"] == server_id), None)
    if server:
        await cb.message.edit_text(
            fmt.fmt_server(server),
            reply_markup=kb.server_actions_menu(server_id),
            parse_mode="HTML"
        )
    else:
        await cb.message.edit_text("вќЊ РЎРµСЂРІРµСЂ РЅРµ РЅР°Р№РґРµРЅ", reply_markup=kb.timeweb_menu())


@router.callback_query(F.data.startswith("reboot_"))
async def cb_reboot(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[1])
    await cb.answer("вЏі РџРµСЂРµР·Р°РіСЂСѓР¶Р°СЋ...")
    success = await tw.reboot_server(server_id)
    text = "вњ… РљРѕРјР°РЅРґР° РїРµСЂРµР·Р°РіСЂСѓР·РєРё РѕС‚РїСЂР°РІР»РµРЅР°" if success else "вќЊ РћС€РёР±РєР° РїРµСЂРµР·Р°РіСЂСѓР·РєРё"
    await cb.message.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


@router.callback_query(F.data == "tw_domains")
async def cb_tw_domains(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    domains = await tw.get_domains()
    await cb.message.edit_text(
        fmt.fmt_domains(domains),
        reply_markup=kb.timeweb_menu(),
        parse_mode="HTML"
    )


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ Callback: PolzaAI в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.callback_query(F.data == "menu_polzaai")
async def cb_menu_polzaai(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    data = await polza.get_balance()
    await cb.message.edit_text(
        fmt.fmt_polzaai_balance(data),
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ Callback: РЇРЅРґРµРєСЃ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.callback_query(F.data == "menu_yandex")
async def cb_menu_yandex(cb: CallbackQuery):
    await cb.message.edit_text(
        "рџ”Ќ <b>РЇРЅРґРµРєСЃ Р’РµР±РјР°СЃС‚РµСЂ</b>\n\nР’С‹Р±РµСЂРёС‚Рµ СЂР°Р·РґРµР»:",
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "yx_indexing")
async def cb_yx_indexing(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    data = await yx.get_indexing_stats()
    await cb.message.edit_text(
        fmt.fmt_yandex_indexing(data),
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yx_queries")
async def cb_yx_queries(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    data = await yx.get_search_queries()
    await cb.message.edit_text(
        fmt.fmt_yandex_queries(data),
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yx_errors")
async def cb_yx_errors(cb: CallbackQuery):
    await cb.answer("вЏі Р—Р°РїСЂР°С€РёРІР°СЋ...")
    data = await yx.get_errors()
    await cb.message.edit_text(
        fmt.fmt_yandex_errors(data),
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ Callback: РџРѕР»РЅС‹Р№ РѕС‚С‡С‘С‚ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.callback_query(F.data == "full_report")
async def cb_full_report(cb: CallbackQuery):
    await cb.answer("вЏі РЎРѕР±РёСЂР°СЋ РѕС‚С‡С‘С‚...")
    await send_full_report(cb.message.chat.id, cb.bot, cb.message)


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ РЈС‚РёР»РёС‚Р°: РѕС‚РїСЂР°РІРёС‚СЊ РїРѕР»РЅС‹Р№ РѕС‚С‡С‘С‚ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

async def send_full_report(chat_id: int, bot, message=None):
    tw_bal, polzaai_bal, indexing, queries = await asyncio.gather(
        tw.get_account_balance(),
        polza.get_balance(),
        yx.get_indexing_stats(),
        yx.get_search_queries(),
    )
    text = fmt.fmt_full_report(tw_bal, polzaai_bal, indexing, queries)
    if message:
        await message.edit_text(text, reply_markup=kb.main_menu(), parse_mode="HTML")
    else:
        await bot.send_message(chat_id, text, reply_markup=kb.main_menu(), parse_mode="HTML")
