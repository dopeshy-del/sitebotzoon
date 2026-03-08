import aiohttp
from datetime import datetime, timedelta, timezone
from config import TIMEWEB_API_TOKEN, TIMEWEB_API_URL


HEADERS = {
    "Authorization": f"Bearer {TIMEWEB_API_TOKEN}",
    "Content-Type": "application/json",
}


async def get_account_balance() -> dict:
    """Получить баланс аккаунта TimeWeb."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/account/finances", headers=HEADERS) as r:
            if r.status != 200:
                return {"error": f"HTTP {r.status}"}
            data = await r.json()
            finances = data.get("finances", {})
            daily_burn = _extract_daily_burn(finances)
            runway = _estimate_runway(finances.get("balance", 0), daily_burn)
            return {
                "balance": finances.get("balance", 0),
                "currency": "₽",
                "bonus": finances.get("bonus_balance", 0),
                "daily_burn": daily_burn,
                "runway_days": runway.get("runway_days"),
                "runway_date": runway.get("runway_date"),
            }


def _extract_daily_burn(finances: dict) -> float:
    """Попытаться извлечь дневные списания из разных полей ответа API."""
    for key in (
        "daily_writeoff",
        "daily_cost",
        "writeoff_per_day",
        "expenses_per_day",
        "cost_per_day",
    ):
        value = finances.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def _estimate_runway(balance: float, daily_burn: float) -> dict:
    """Посчитать через сколько дней/дату баланс станет 0."""
    if daily_burn <= 0:
        return {"runway_days": None, "runway_date": None}

    runway_days = round(balance / daily_burn, 1)
    depletion_date = datetime.now(timezone.utc) + timedelta(days=runway_days)
    return {
        "runway_days": runway_days,
        "runway_date": depletion_date.date().isoformat(),
    }


async def get_servers() -> list:
    """Получить список VPS серверов."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/servers", headers=HEADERS) as r:
            data = await r.json()
            servers = data.get("servers", [])
            result = []
            for s in servers:
                result.append({
                    "id": s.get("id"),
                    "name": s.get("name", "—"),
                    "status": s.get("status", "unknown"),
                    "cpu": s.get("cpu", 0),
                    "ram": s.get("ram", 0),
                    "disk": s.get("hdd", 0),
                    "ip": s.get("networks", [{}])[0].get("ips", [{}])[0].get("ip", "—")
                            if s.get("networks") else "—",
                    "location": s.get("location", "—"),
                    "os": s.get("os", {}).get("name", "—"),
                })
            return result


async def get_server_stats(server_id: int) -> dict:
    """Получить статистику конкретного сервера."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{TIMEWEB_API_URL}/servers/{server_id}/statistics",
            headers=HEADERS
        ) as r:
            return await r.json()


async def reboot_server(server_id: int) -> bool:
    """Перезагрузить сервер."""
    return await _run_server_action(server_id, "reboot")


async def soft_reboot_server(server_id: int) -> bool:
    """Выполнить мягкую перезагрузку сервера."""
    return await _run_server_action(server_id, "soft_reboot", fallback_actions=("reboot_soft", "reboot"))


async def start_server(server_id: int) -> bool:
    """Включить сервер."""
    return await _run_server_action(server_id, "start", fallback_actions=("power_on", "resume"))


async def stop_server(server_id: int) -> bool:
    """Выключить сервер."""
    return await _run_server_action(server_id, "shutdown", fallback_actions=("stop", "power_off"))


async def get_domains() -> list:
    """Получить список доменов."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/domains", headers=HEADERS) as r:
            data = await r.json()
            domains = data.get("domains", [])
            return [
                {
                    "fqdn": d.get("fqdn", "—"),
                    "status": d.get("status", "—"),
                    "expires": d.get("expiration", "—"),
                }
                for d in domains
            ]


async def get_products_summary() -> dict:
    """Получить сводку по стоимости активных сервисов Timeweb."""
    async with aiohttp.ClientSession() as session:
        # Актуальный API Timeweb: /account/services/cost.
        # В разных аккаунтах структура payload может отличаться (в т.ч. через projects),
        # поэтому собираем элементы стоимости рекурсивно.
        services_costs = await _fetch_services_costs(session)
        if services_costs:
            return _summarize_services_costs(services_costs)

        # Fallback на старую логику, если endpoint недоступен.
        return await _get_products_summary_fallback(session)


async def _fetch_services_costs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(f"{TIMEWEB_API_URL}/account/services/cost", headers=HEADERS) as r:
            if r.status != 200:
                return []
            payload = await r.json()
            return _extract_cost_items(payload)
    except aiohttp.ClientError:
        return []
    return []


def _extract_cost_items(payload: dict) -> list[dict]:
    """Извлечь нормализованный список сервисов с ценой из любого payload Timeweb."""
    collected: list[dict] = []
    seen_signatures: set[tuple[str, float]] = set()

    def walk(value):
        if isinstance(value, dict):
            normalized = _normalize_cost_item(value)
            if normalized:
                signature = (normalized["name"], normalized["monthly_cost"])
                if signature not in seen_signatures:
                    seen_signatures.add(signature)
                    collected.append(normalized)

            for nested_value in value.values():
                walk(nested_value)
            return

        if isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return collected


def _normalize_cost_item(item: dict) -> dict | None:
    cost = _extract_service_cost(item)
    if cost <= 0:
        return None

    # Отсекаем агрегаты вида total_monthly_cost, чтобы не задвоить суммы.
    if any(key in item for key in ("total_monthly_cost", "estimated_daily_cost", "total_cost")):
        has_detailed_list = any(isinstance(v, list) and v for v in item.values())
        if has_detailed_list:
            return None

    name = _extract_service_name(item)
    return {
        "name": name,
        "monthly_cost": round(cost, 2),
    }


def _summarize_services_costs(services_costs: list[dict]) -> dict:
    products_by_name: dict[str, dict] = {}

    for item in services_costs:
        service_name = _extract_service_name(item)
        cost = _extract_service_cost(item)

        if service_name not in products_by_name:
            products_by_name[service_name] = {
                "name": service_name,
                "count": 0,
                "monthly_cost": 0.0,
            }

        products_by_name[service_name]["count"] += 1
        products_by_name[service_name]["monthly_cost"] += cost

    products = sorted(
        (
            {
                "name": product["name"],
                "count": product["count"],
                "monthly_cost": round(product["monthly_cost"], 2),
            }
            for product in products_by_name.values()
        ),
        key=lambda product: product["monthly_cost"],
        reverse=True,
    )

    total_monthly = sum(product["monthly_cost"] for product in products)
    return {
        "products": products,
        "total_monthly_cost": round(total_monthly, 2),
        "estimated_daily_cost": round(total_monthly / 30, 2) if total_monthly else 0.0,
    }


def _extract_service_name(item: dict) -> str:
    for key in (
        "service_name",
        "name",
        "slug",
        "service",
        "title",
        "project_name",
        "type",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Прочие сервисы"


def _extract_service_cost(item: dict) -> float:
    for key in (
        "monthly_cost",
        "cost_per_month",
        "month_price",
        "price_per_month",
        "monthly_payment",
        "cost_month",
        "cost",
        "price",
    ):
        value = item.get(key)
        if isinstance(value, (int, float)):
            return float(value)

    for value in item.values():
        if isinstance(value, dict):
            nested = _extract_service_cost(value)
            if nested > 0:
                return nested

    return 0.0


async def _get_products_summary_fallback(session: aiohttp.ClientSession) -> dict:
    endpoints = {
        "VPS": "/servers",
        "Домены": "/domains",
        "Базы данных": "/databases",
        "Объектное хранилище": "/s3/buckets",
        "Балансировщики": "/balancers",
        "Kubernetes": "/k8s/clusters",
    }

    products = []
    total_monthly = 0.0
    for title, endpoint in endpoints.items():
        try:
            async with session.get(f"{TIMEWEB_API_URL}{endpoint}", headers=HEADERS) as r:
                if r.status != 200:
                    continue
                payload = await r.json()
                count, monthly_cost = _parse_product_payload(payload)
                if count == 0 and monthly_cost == 0:
                    continue
                total_monthly += monthly_cost
                products.append(
                    {
                        "name": title,
                        "count": count,
                        "monthly_cost": round(monthly_cost, 2),
                    }
                )
        except aiohttp.ClientError:
            continue

    return {
        "products": products,
        "total_monthly_cost": round(total_monthly, 2),
        "estimated_daily_cost": round(total_monthly / 30, 2) if total_monthly else 0.0,
    }


def _parse_product_payload(payload: dict) -> tuple[int, float]:
    items = []
    for value in payload.values():
        if isinstance(value, list):
            items = value
            break

    monthly_cost = 0.0
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in ("monthly_cost", "cost_per_month", "price_per_month", "month_price"):
            val = item.get(key)
            if isinstance(val, (int, float)):
                monthly_cost += float(val)
                break
    return len(items), monthly_cost


async def _run_server_action(server_id: int, action: str, fallback_actions: tuple[str, ...] = ()) -> bool:
    actions = (action, *fallback_actions)
    async with aiohttp.ClientSession() as session:
        for action_name in actions:
            try:
                async with session.post(
                    f"{TIMEWEB_API_URL}/servers/{server_id}/action",
                    headers=HEADERS,
                    json={"action": action_name}
                ) as r:
                    if r.status in (200, 202, 204):
                        return True
                    # Если экшен не поддерживается, пробуем fallback.
                    if r.status in (400, 404, 422):
                        continue
            except aiohttp.ClientError:
                continue
    return False
