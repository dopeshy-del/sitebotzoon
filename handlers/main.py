import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import api.timeweb as tw
import api.polzaai as polza
import api.yandex_webmaster as yx
import api.cursor as cursor
import keyboards.inline as kb
import formatters as fmt
from config import CURSOR_ENABLED, CURSOR_API_KEY

router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(
        "👋 <b>Myzoon Monitor Bot</b>\n\n"
        "Мониторинг и управление вашей инфраструктурой.\n"
        "Выберите раздел:",
        reply_markup=kb.main_menu(),
        parse_mode="HTML"
    )


# /status
@router.message(Command("status"))
async def cmd_status(msg: Message):
    wait = await msg.answer("⏳ Собираю данные...")
    servers = await tw.get_servers()
    text = fmt.fmt_servers_list(servers)
    await wait.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


# /balance
@router.message(Command("balance"))
async def cmd_balance(msg: Message):
    wait = await msg.answer("⏳ Запрашиваю балансы...")
    tw_bal, tw_products, polzaai_bal, polza_usage = await asyncio.gather(
        tw.get_account_balance(),
        tw.get_products_summary(),
        polza.get_balance(),
        polza.get_usage_stats(),
    )
    text = (
        fmt.fmt_timeweb_balance(tw_bal)
        + "\n\n"
        + fmt.fmt_timeweb_products(tw_products)
        + "\n\n"
        + fmt.fmt_polzaai_balance(polzaai_bal)
        + "\n\n"
        + fmt.fmt_polzaai_usage(polza_usage)
    )
    await wait.edit_text(text, reply_markup=kb.back_to_main(), parse_mode="HTML")




# /cursor
@router.message(Command("cursor"))
async def cmd_cursor(msg: Message):
    if not CURSOR_ENABLED:
        await msg.answer(
            "⚠️ Мониторинг Cursor выключен. Установите <code>CURSOR_ENABLED=true</code> в .env",
            parse_mode="HTML",
        )
        return
    if not CURSOR_API_KEY:
        await msg.answer(
            "⚠️ Не задан <code>CURSOR_API_KEY</code>. Добавьте ключ в .env.",
            parse_mode="HTML",
        )
        return

    wait = await msg.answer("⏳ Проверяю Cursor API...")
    limits = await cursor.get_limits()
    text = fmt.fmt_cursor_limits(limits)
    await wait.edit_text(text, reply_markup=kb.back_to_main(), parse_mode="HTML")


# /report
@router.message(Command("report"))
async def cmd_report(msg: Message):
    await send_full_report(msg.chat.id, msg.bot)


# Callback: главное меню
@router.callback_query(F.data == "main_menu")
async def cb_main_menu(cb: CallbackQuery):
    await cb.message.edit_text(
        "👋 <b>Myzoon Monitor Bot</b>\n\nВыберите раздел:",
        reply_markup=kb.main_menu(),
        parse_mode="HTML"
    )
    await cb.answer()


# Callback: TimeWeb
@router.callback_query(F.data == "menu_timeweb")
async def cb_menu_timeweb(cb: CallbackQuery):
    await cb.message.edit_text(
        "☁️ <b>TimeWeb Cloud</b>\n\nВыберите раздел:",
        reply_markup=kb.timeweb_menu(),
        parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "tw_balance")
async def cb_tw_balance(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    data, products = await asyncio.gather(tw.get_account_balance(), tw.get_products_summary())
    await cb.message.edit_text(
        fmt.fmt_timeweb_balance(data) + "\n\n" + fmt.fmt_timeweb_products(products),
        reply_markup=kb.timeweb_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tw_servers")
async def cb_tw_servers(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    servers = await tw.get_servers()
    await cb.message.edit_text(
        fmt.fmt_servers_list(servers),
        reply_markup=kb.servers_menu(servers),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("server_"))
async def cb_server_detail(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[1])
    await cb.answer("⏳")
    servers = await tw.get_servers()
    server = next((s for s in servers if s["id"] == server_id), None)
    if server:
        await cb.message.edit_text(
            fmt.fmt_server(server),
            reply_markup=kb.server_actions_menu(server_id),
            parse_mode="HTML"
        )
    else:
        await cb.message.edit_text("❌ Сервер не найден", reply_markup=kb.timeweb_menu())


@router.callback_query(F.data.startswith("reboot_"))
async def cb_reboot(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[1])
    await cb.answer("⏳ Перезагружаю...")
    success = await tw.reboot_server(server_id)
    text = "✅ Команда перезагрузки отправлена" if success else "❌ Ошибка перезагрузки"
    await cb.message.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


@router.callback_query(F.data.startswith("soft_reboot_"))
async def cb_soft_reboot(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[-1])
    await cb.answer("⏳ Мягко перезагружаю...")
    success = await tw.soft_reboot_server(server_id)
    text = "✅ Команда мягкой перезагрузки отправлена" if success else "❌ Ошибка мягкой перезагрузки"
    await cb.message.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


@router.callback_query(F.data.startswith("start_"))
async def cb_start_server(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[1])
    await cb.answer("⏳ Включаю сервер...")
    success = await tw.start_server(server_id)
    text = "✅ Команда на включение отправлена" if success else "❌ Ошибка включения сервера"
    await cb.message.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


@router.callback_query(F.data.startswith("stop_"))
async def cb_stop_server(cb: CallbackQuery):
    server_id = int(cb.data.split("_")[1])
    await cb.answer("⏳ Выключаю сервер...")
    success = await tw.stop_server(server_id)
    text = "✅ Команда на выключение отправлена" if success else "❌ Ошибка выключения сервера"
    await cb.message.edit_text(text, reply_markup=kb.timeweb_menu(), parse_mode="HTML")


@router.callback_query(F.data == "tw_domains")
async def cb_tw_domains(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    domains = await tw.get_domains()
    await cb.message.edit_text(
        fmt.fmt_domains(domains),
        reply_markup=kb.timeweb_menu(),
        parse_mode="HTML"
    )


# Callback: PolzaAI
@router.callback_query(F.data == "menu_polzaai")
async def cb_menu_polzaai(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    data, usage = await asyncio.gather(polza.get_balance(), polza.get_usage_stats())
    await cb.message.edit_text(
        fmt.fmt_polzaai_balance(data) + "\n\n" + fmt.fmt_polzaai_usage(usage),
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )


# Callback: Яндекс
@router.callback_query(F.data == "menu_yandex")
async def cb_menu_yandex(cb: CallbackQuery):
    await cb.message.edit_text(
        "🔍 <b>Яндекс Вебмастер</b>\n\nВыберите раздел:",
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "yx_indexing")
async def cb_yx_indexing(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    data = await yx.get_indexing_stats()
    await cb.message.edit_text(
        fmt.fmt_yandex_indexing(data),
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yx_queries")
async def cb_yx_queries(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    data = await yx.get_search_queries()
    await cb.message.edit_text(
        fmt.fmt_yandex_queries(data),
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yx_errors")
async def cb_yx_errors(cb: CallbackQuery):
    await cb.answer("⏳ Запрашиваю...")
    data = await yx.get_errors()
    await cb.message.edit_text(
        fmt.fmt_yandex_errors(data),
        reply_markup=kb.yandex_menu(),
        parse_mode="HTML"
    )


# Callback: полный отчёт
@router.callback_query(F.data == "full_report")
async def cb_full_report(cb: CallbackQuery):
    await cb.answer("⏳ Собираю отчёт...")
    await send_full_report(cb.message.chat.id, cb.bot, cb.message)


# Утилита: отправить полный отчёт
async def send_full_report(chat_id: int, bot, message=None):
    tw_bal, tw_products, polzaai_bal, polza_usage, indexing, queries = await asyncio.gather(
        tw.get_account_balance(),
        tw.get_products_summary(),
        polza.get_balance(),
        polza.get_usage_stats(),
        yx.get_indexing_stats(),
        yx.get_search_queries(),
    )
    text = fmt.fmt_full_report(tw_bal, tw_products, polzaai_bal, polza_usage, indexing, queries)
    if message:
        await message.edit_text(text, reply_markup=kb.main_menu(), parse_mode="HTML")
    else:
        await bot.send_message(chat_id, text, reply_markup=kb.main_menu(), parse_mode="HTML")
