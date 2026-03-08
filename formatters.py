from datetime import datetime


def fmt_timeweb_balance(data: dict) -> str:
    if "error" in data:
        return f"❌ Ошибка получения баланса TimeWeb: {data['error']}"
    runway_line = "♾️ Списания не обнаружены"
    if data.get("runway_days") is not None:
        runway_line = (
            f"⏳ Хватит на: <b>{data['runway_days']} дн.</b> "
            f"(до {data.get('runway_date', '—')})"
        )
    return (
        f"💰 <b>Баланс TimeWeb Cloud</b>\n\n"
        f"💵 Основной: <b>{data['balance']} {data['currency']}</b>\n"
        f"🎁 Бонусы: <b>{data['bonus']} {data['currency']}</b>\n"
        f"📉 Списания/день: <b>{data.get('daily_burn', 0)} {data['currency']}</b>\n"
        f"{runway_line}"
    )


def fmt_timeweb_products(data: dict) -> str:
    products = data.get("products", [])
    if not products:
        return "📦 <b>Продукты TimeWeb</b>\n\nНет данных по продуктам."

    lines = ["📦 <b>Продукты TimeWeb</b>\n"]
    for product in products:
        price = product.get("monthly_cost", 0)
        if price:
            lines.append(f"• {product['name']}: {product['count']} шт. (~{price} ₽/мес)")
        else:
            lines.append(f"• {product['name']}: {product['count']} шт.")

    lines.append("")
    lines.append(f"Итого: ~<b>{data.get('total_monthly_cost', 0)} ₽/мес</b>")
    lines.append(f"В день: ~<b>{data.get('estimated_daily_cost', 0)} ₽</b>")
    return "\n".join(lines)


def fmt_server(s: dict) -> str:
    status_icon = "🟢 Работает" if s["status"] == "on" else "🔴 Выключен"
    return (
        f"🖥️ <b>{s['name']}</b>\n"
        f"├ Статус: {status_icon}\n"
        f"├ IP: <code>{s['ip']}</code>\n"
        f"├ CPU: {s['cpu']} ядер\n"
        f"├ RAM: {s['ram']} МБ\n"
        f"├ Диск: {s['disk']} ГБ\n"
        f"├ ОС: {s['os']}\n"
        f"└ Локация: {s['location']}"
    )


def fmt_servers_list(servers: list) -> str:
    if not servers:
        return "🖥️ Серверы не найдены"
    lines = ["🖥️ <b>Серверы TimeWeb Cloud</b>\n"]
    for s in servers:
        icon = "🟢" if s["status"] == "on" else "🔴"
        lines.append(f"{icon} <b>{s['name']}</b> — <code>{s['ip']}</code>")
    return "\n".join(lines)


def fmt_domains(domains: list) -> str:
    if not domains:
        return "🌐 Домены не найдены"
    lines = ["🌐 <b>Домены TimeWeb Cloud</b>\n"]
    for d in domains:
        lines.append(f"• <b>{d['fqdn']}</b> — {d['status']} (до {d['expires'][:10] if d['expires'] != '—' else '—'})")
    return "\n".join(lines)


def fmt_polzaai_balance(data: dict) -> str:
    if "error" in data:
        return f"❌ Ошибка получения баланса PolzaAI: {data['error']}"
    used = data.get("requests_used", 0)
    limit = data.get("requests_limit", 0)
    bar = f"{used}/{limit}" if limit else "—"
    return (
        f"🤖 <b>PolzaAI</b>\n\n"
        f"💵 Баланс: <b>{data['balance']} {data['currency']}</b>\n"
        f"📦 Тариф: <b>{data['plan']}</b>\n"
        f"📊 Запросы: <b>{bar}</b>"
    )


def fmt_polzaai_usage(data: dict) -> str:
    if "error" in data and not data.get("keys"):
        return f"⚠️ <b>Polza AI usage</b>\n\n{data['error']}"

    lines = ["📊 <b>Polza AI: использование ключей</b>\n"]
    for i, item in enumerate(data.get("keys", []), 1):
        lines.append(
            f"{i}. <b>{item['key_name']}</b> ({item['model']})\n"
            f"   • Запросы: {item['requests']}\n"
            f"   • Токены: {item['tokens']}\n"
            f"   • Расход: {item['cost']} ₽"
        )

    totals = data.get("totals", {})
    lines.append("")
    lines.append(
        f"Σ Запросы: <b>{totals.get('requests', 0)}</b> | "
        f"Токены: <b>{totals.get('tokens', 0)}</b> | "
        f"Расход: <b>{totals.get('cost', 0)} ₽</b>"
    )
    return "\n".join(lines)


def fmt_yandex_indexing(data: dict) -> str:
    if "error" in data:
        return f"❌ Ошибка Яндекс Вебмастера: {data['error']}"
    return (
        f"📈 <b>Индексация Яндекс</b>\n\n"
        f"✅ Проиндексировано: <b>{data['indexed_count']:,}</b> стр.\n"
        f"❌ Исключено: <b>{data['excluded_count']:,}</b> стр."
    )


def fmt_yandex_queries(data: dict) -> str:
    if "error" in data:
        return f"❌ Ошибка: {data['error']}"
    lines = [f"🔎 <b>Топ запросов</b> ({data['period']})\n"]
    for i, q in enumerate(data["top_queries"], 1):
        lines.append(
            f"{i}. <b>{q['query']}</b>\n"
            f"   👆 {q['clicks']} кл. | 👁 {q['impressions']} пок. | "
            f"CTR {q['ctr']}% | #{q['position']}"
        )
    return "\n".join(lines)


def fmt_yandex_errors(data: dict) -> str:
    if "error" in data:
        return f"❌ Ошибка: {data['error']}"
    states = data.get("states", [])
    if not states:
        return "✅ <b>Ошибок не обнаружено</b>"
    lines = ["⚠️ <b>Проблемы сайта</b>\n"]
    for s in states:
        lines.append(f"• {s.get('state', '—')}: {s.get('message', '—')}")
    return "\n".join(lines)


def fmt_full_report(tw_balance, tw_products, polzaai, polza_usage, indexing, queries) -> str:
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    parts = [
        f"📊 <b>Полный отчёт</b> | {now}\n",
        "━━━━━━━━━━━━━━━━━━━━",
        fmt_timeweb_balance(tw_balance),
        "━━━━━━━━━━━━━━━━━━━━",
        fmt_timeweb_products(tw_products),
        "━━━━━━━━━━━━━━━━━━━━",
        fmt_polzaai_balance(polzaai),
        "━━━━━━━━━━━━━━━━━━━━",
        fmt_polzaai_usage(polza_usage),
        "━━━━━━━━━━━━━━━━━━━━",
        fmt_yandex_indexing(indexing),
    ]
    if queries and "top_queries" in queries and queries["top_queries"]:
        top = queries["top_queries"][0]
        parts.append(f"\n🔎 Топ запрос: <b>{top['query']}</b> ({top['clicks']} кл.)")
    return "\n".join(parts)
