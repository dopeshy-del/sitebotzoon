from datetime import datetime


def fmt_timeweb_balance(data: dict) -> str:
    if "error" in data:
        return f"вќЊ РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ Р±Р°Р»Р°РЅСЃР° TimeWeb: {data['error']}"
    return (
        f"рџ’° <b>Р‘Р°Р»Р°РЅСЃ TimeWeb Cloud</b>\n\n"
        f"рџ’µ РћСЃРЅРѕРІРЅРѕР№: <b>{data['balance']} {data['currency']}</b>\n"
        f"рџЋЃ Р‘РѕРЅСѓСЃС‹: <b>{data['bonus']} {data['currency']}</b>"
    )


def fmt_server(s: dict) -> str:
    status_icon = "рџџў Р Р°Р±РѕС‚Р°РµС‚" if s["status"] == "on" else "рџ”ґ Р’С‹РєР»СЋС‡РµРЅ"
    return (
        f"рџ–ҐпёЏ <b>{s['name']}</b>\n"
        f"в”њ РЎС‚Р°С‚СѓСЃ: {status_icon}\n"
        f"в”њ IP: <code>{s['ip']}</code>\n"
        f"в”њ CPU: {s['cpu']} СЏРґРµСЂ\n"
        f"в”њ RAM: {s['ram']} РњР‘\n"
        f"в”њ Р”РёСЃРє: {s['disk']} Р“Р‘\n"
        f"в”њ РћРЎ: {s['os']}\n"
        f"в”” Р›РѕРєР°С†РёСЏ: {s['location']}"
    )


def fmt_servers_list(servers: list) -> str:
    if not servers:
        return "рџ–ҐпёЏ РЎРµСЂРІРµСЂС‹ РЅРµ РЅР°Р№РґРµРЅС‹"
    lines = ["рџ–ҐпёЏ <b>РЎРµСЂРІРµСЂС‹ TimeWeb Cloud</b>\n"]
    for s in servers:
        icon = "рџџў" if s["status"] == "on" else "рџ”ґ"
        lines.append(f"{icon} <b>{s['name']}</b> вЂ” <code>{s['ip']}</code>")
    return "\n".join(lines)


def fmt_domains(domains: list) -> str:
    if not domains:
        return "рџЊђ Р”РѕРјРµРЅС‹ РЅРµ РЅР°Р№РґРµРЅС‹"
    lines = ["рџЊђ <b>Р”РѕРјРµРЅС‹ TimeWeb Cloud</b>\n"]
    for d in domains:
        lines.append(f"вЂў <b>{d['fqdn']}</b> вЂ” {d['status']} (РґРѕ {d['expires'][:10] if d['expires'] != 'вЂ”' else 'вЂ”'})")
    return "\n".join(lines)


def fmt_polzaai_balance(data: dict) -> str:
    if "error" in data:
        return f"вќЊ РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ Р±Р°Р»Р°РЅСЃР° PolzaAI: {data['error']}"
    used = data.get("requests_used", 0)
    limit = data.get("requests_limit", 0)
    bar = f"{used}/{limit}" if limit else "вЂ”"
    return (
        f"рџ¤– <b>PolzaAI</b>\n\n"
        f"рџ’µ Р‘Р°Р»Р°РЅСЃ: <b>{data['balance']} {data['currency']}</b>\n"
        f"рџ“¦ РўР°СЂРёС„: <b>{data['plan']}</b>\n"
        f"рџ“Љ Р—Р°РїСЂРѕСЃС‹: <b>{bar}</b>"
    )


def fmt_yandex_indexing(data: dict) -> str:
    if "error" in data:
        return f"вќЊ РћС€РёР±РєР° РЇРЅРґРµРєСЃ Р’РµР±РјР°СЃС‚РµСЂР°: {data['error']}"
    return (
        f"рџ“€ <b>РРЅРґРµРєСЃР°С†РёСЏ РЇРЅРґРµРєСЃ</b>\n\n"
        f"вњ… РџСЂРѕРёРЅРґРµРєСЃРёСЂРѕРІР°РЅРѕ: <b>{data['indexed_count']:,}</b> СЃС‚СЂ.\n"
        f"вќЊ РСЃРєР»СЋС‡РµРЅРѕ: <b>{data['excluded_count']:,}</b> СЃС‚СЂ."
    )


def fmt_yandex_queries(data: dict) -> str:
    if "error" in data:
        return f"вќЊ РћС€РёР±РєР°: {data['error']}"
    lines = [f"рџ”Ћ <b>РўРѕРї Р·Р°РїСЂРѕСЃРѕРІ</b> ({data['period']})\n"]
    for i, q in enumerate(data["top_queries"], 1):
        lines.append(
            f"{i}. <b>{q['query']}</b>\n"
            f"   рџ‘† {q['clicks']} РєР». | рџ‘Ѓ {q['impressions']} РїРѕРє. | "
            f"CTR {q['ctr']}% | #{q['position']}"
        )
    return "\n".join(lines)


def fmt_yandex_errors(data: dict) -> str:
    if "error" in data:
        return f"вќЊ РћС€РёР±РєР°: {data['error']}"
    states = data.get("states", [])
    if not states:
        return "вњ… <b>РћС€РёР±РѕРє РЅРµ РѕР±РЅР°СЂСѓР¶РµРЅРѕ</b>"
    lines = ["вљ пёЏ <b>РџСЂРѕР±Р»РµРјС‹ СЃР°Р№С‚Р°</b>\n"]
    for s in states:
        lines.append(f"вЂў {s.get('state', 'вЂ”')}: {s.get('message', 'вЂ”')}")
    return "\n".join(lines)


def fmt_full_report(tw_balance, polzaai, indexing, queries) -> str:
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    parts = [
        f"рџ“Љ <b>РџРѕР»РЅС‹Р№ РѕС‚С‡С‘С‚</b> | {now}\n",
        "в”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓ",
        fmt_timeweb_balance(tw_balance),
        "в”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓ",
        fmt_polzaai_balance(polzaai),
        "в”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓ",
        fmt_yandex_indexing(indexing),
    ]
    if queries and "top_queries" in queries and queries["top_queries"]:
        top = queries["top_queries"][0]
        parts.append(f"\nрџ”Ћ РўРѕРї Р·Р°РїСЂРѕСЃ: <b>{top['query']}</b> ({top['clicks']} РєР».)")
    return "\n".join(parts)
