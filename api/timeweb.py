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
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{TIMEWEB_API_URL}/servers/{server_id}/action",
            headers=HEADERS,
            json={"action": "reboot"}
        ) as r:
            return r.status == 200


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
    """Получить список основных продуктов аккаунта Timeweb и расходы по ним (если есть в API)."""
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
    async with aiohttp.ClientSession() as session:
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
