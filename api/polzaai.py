import aiohttp
from config import POLZAAI_API_KEY, POLZAAI_API_URL

HEADERS = {
    "Authorization": f"Bearer {POLZAAI_API_KEY}",
}

BASE_URLS = [POLZAAI_API_URL.rstrip("/")]
if "api.polza.ai" in BASE_URLS[0]:
    BASE_URLS.append("https://polza.ai/api/v1")

async def get_balance() -> dict:
    async with aiohttp.ClientSession() as session:
        for base_url in BASE_URLS:
            async with session.get(f"{base_url}/balance", headers=HEADERS) as r:
                if r.status == 200:
                    data = await r.json()
                    return {
                        "balance": float(data.get("amount", 0)),
                        "currency": "₽",
                        "plan": "—",
                        "requests_used": 0,
                        "requests_limit": 0,
                    }
        return {"error": "Не удалось получить баланс", "balance": None}


async def get_usage_stats() -> dict:
    """Получить метрики использования API-ключей Polza AI."""
    endpoint_candidates = (
        "/usage",
        "/statistics/usage",
        "/api-keys/usage",
        "/keys/usage",
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
                        if parsed["keys"]:
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

    total_requests = 0
    total_tokens = 0
    total_cost = 0.0
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

    return {
        "keys": keys,
        "totals": {
            "requests": total_requests,
            "tokens": total_tokens,
            "cost": round(total_cost, 4),
        },
    }


def _extract_items(payload: dict) -> list:
    for key in ("items", "data", "usage", "api_keys", "keys", "stats"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    if isinstance(payload, list):
        return payload
    return []
