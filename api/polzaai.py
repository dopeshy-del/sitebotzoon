import aiohttp
from config import POLZAAI_API_KEY

HEADERS = {
    "Authorization": f"Bearer {POLZAAI_API_KEY}",
}

async def get_balance() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://polza.ai/api/v1/balance",
            headers=HEADERS
        ) as r:
            if r.status == 200:
                data = await r.json()
                return {
                    "balance": float(data.get("amount", 0)),
                    "currency": "₽",
                    "plan": "—",
                    "requests_used": 0,
                    "requests_limit": 0,
                }
            else:
                return {"error": f"HTTP {r.status}", "balance": None}

async def get_usage_stats() -> dict:
    return {}
