import aiohttp
from config import POLZAAI_API_KEY, POLZAAI_USER_ID, POLZAAI_API_URL


HEADERS = {
    "Authorization": f"Bearer {POLZAAI_API_KEY}",
    "Content-Type": "application/json",
}


async def get_balance() -> dict:
    """Получить баланс PolzaAI."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{POLZAAI_API_URL}/users/{POLZAAI_USER_ID}/balance",
            headers=HEADERS
        ) as r:
            if r.status == 200:
                data = await r.json()
                return {
                    "balance": data.get("balance", 0),
                    "currency": data.get("currency", "₽"),
                    "plan": data.get("plan", "—"),
                    "requests_used": data.get("requests_used", 0),
                    "requests_limit": data.get("requests_limit", 0),
                }
            else:
                return {"error": f"HTTP {r.status}", "balance": None}


async def get_usage_stats() -> dict:
    """Получить статистику использования."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{POLZAAI_API_URL}/users/{POLZAAI_USER_ID}/stats",
            headers=HEADERS
        ) as r:
            if r.status == 200:
                return await r.json()
            return {"error": f"HTTP {r.status}"}
