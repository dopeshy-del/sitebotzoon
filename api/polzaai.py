import aiohttp
from config import POLZAAI_API_KEY, POLZAAI_API_URL

HEADERS = {
    "Authorization": f"Bearer {POLZAAI_API_KEY}",
}

BASE_URLS = [POLZAAI_API_URL.rstrip("/")]
# По документации рабочий endpoint баланса: https://polza.ai/api/v1/balance
if "polza.ai/api/v1" not in BASE_URLS:
    BASE_URLS.insert(0, "https://polza.ai/api/v1")
if "api.polza.ai/v1" not in BASE_URLS:
    BASE_URLS.append("https://api.polza.ai/v1")

async def get_balance() -> dict:
    async with aiohttp.ClientSession() as session:
        for base_url in BASE_URLS:
            try:
                async with session.get(f"{base_url}/balance", headers=HEADERS) as r:
                    if r.status != 200:
                        continue
                    data = await r.json()
                    amount = data.get("amount", data.get("balance", 0))
                    return {
                        "balance": float(amount),
                        "currency": data.get("currency") or "₽",
                        "plan": data.get("plan") or "—",
                        "requests_used": int(data.get("requests_used") or 0),
                        "requests_limit": int(data.get("requests_limit") or 0),
                    }
            except (aiohttp.ClientError, ValueError, TypeError):
                continue
        return {"error": "Не удалось получить баланс", "balance": None}


async def get_usage_stats() -> dict:
    """Получить метрики использования API-ключей Polza AI."""
    endpoint_candidates = (
        "/usage",
        "/usage/stats",
        "/usage/summary",
        "/statistics/usage",
        "/statistics",
        "/api-keys/usage",
        "/keys/usage",
        "/billing/usage",
    )

    async with aiohttp.ClientSession() as session:
        for base_url in BASE_URLS:
            for endpoint in endpoint_candidates:
                url = f"{base_url}{endpoint}"
                try:
                    async with session.get(url, headers=HEADERS) as r:
                        if r.status != 200:
                            continue
                        payload = await r.json()
                        parsed = _parse_usage_payload(payload)
                        if parsed["keys"] or any(parsed["totals"].values()):
                            parsed["source_endpoint"] = endpoint
                            return parsed
                except aiohttp.ClientError:
                    continue

    return {
        "keys": [],
        "totals": {
            "requests": 0,
            "tokens": 0,
            "cost": 0.0,
        },
        "error": "Метрики не найдены в известных endpoint'ах API",
    }


def _parse_usage_payload(payload: dict) -> dict:
    keys = []
    items = _extract_items(payload)

    total_requests = int(payload.get("requests") or payload.get("total_requests") or 0)
    total_tokens = int(payload.get("tokens") or payload.get("total_tokens") or 0)
    total_cost = float(payload.get("cost") or payload.get("total_cost") or payload.get("spent") or 0.0)
    for item in items:
        if not isinstance(item, dict):
            continue
        requests = int(item.get("requests") or item.get("requests_count") or item.get("calls") or 0)
        tokens = int(item.get("tokens") or item.get("tokens_used") or item.get("total_tokens") or 0)
        cost = float(item.get("cost") or item.get("cost_rub") or item.get("spent") or 0.0)

        key_name = (
            item.get("key_name")
            or item.get("name")
            or item.get("api_key")
            or item.get("key")
            or "—"
        )
        model = item.get("model") or item.get("provider") or "—"

        keys.append(
            {
                "key_name": key_name,
                "model": model,
                "requests": requests,
                "tokens": tokens,
                "cost": round(cost, 4),
            }
        )

        total_requests += requests
        total_tokens += tokens
        total_cost += cost

    if isinstance(payload.get("totals"), dict):
        totals = payload["totals"]
        total_requests = max(total_requests, int(totals.get("requests") or totals.get("calls") or 0))
        total_tokens = max(total_tokens, int(totals.get("tokens") or totals.get("total_tokens") or 0))
        total_cost = max(total_cost, float(totals.get("cost") or totals.get("spent") or 0.0))

    return {
        "keys": keys,
        "totals": {
            "requests": total_requests,
            "tokens": total_tokens,
            "cost": round(total_cost, 4),
        },
    }


def _extract_items(payload: dict) -> list:
    for key in ("items", "data", "usage", "api_keys", "keys", "stats", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _extract_items(value)
            if nested:
                return nested
    if isinstance(payload, list):
        return payload
    return []
