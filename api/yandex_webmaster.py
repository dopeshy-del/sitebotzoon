import aiohttp
from datetime import datetime, timedelta
from config import YANDEX_OAUTH_TOKEN, YANDEX_USER_ID, YANDEX_HOST_ID, YANDEX_API_URL


HEADERS = {
    "Authorization": f"OAuth {YANDEX_OAUTH_TOKEN}",
}

BASE = f"{YANDEX_API_URL}/user/{YANDEX_USER_ID}/hosts/{YANDEX_HOST_ID}"


async def get_host_info() -> dict:
    """Получить общую информацию о сайте."""
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE, headers=HEADERS) as r:
            if r.status == 200:
                data = await r.json()
                return {
                    "host": data.get("unicode_host_url", "—"),
                    "verified": data.get("verified", False),
                    "main_mirror": data.get("main_mirror", {}).get("unicode_host_url", "—"),
                }
            return {"error": f"HTTP {r.status}"}


async def get_indexing_stats() -> dict:
    """Получить статистику индексации."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE}/indexing/stats", headers=HEADERS) as r:
            if r.status == 200:
                data = await r.json()
                return {
                    "indexed_count": data.get("site_urls_count", {}).get("count", 0),
                    "excluded_count": data.get("excluded_urls_count", {}).get("count", 0),
                }
            return {"error": f"HTTP {r.status}"}


async def get_search_queries() -> dict:
    """Получить статистику поисковых запросов за последние 7 дней."""
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    async with aiohttp.ClientSession() as session:
        params = {
            "date_from": date_from,
            "date_to": date_to,
            "limit": 10,
            "order_by": "TOTAL_CLICKS",
        }
        async with session.get(
            f"{BASE}/search-queries/popular",
            headers=HEADERS,
            params=params
        ) as r:
            if r.status == 200:
                data = await r.json()
                queries = data.get("queries", [])
                return {
                    "period": f"{date_from} — {date_to}",
                    "top_queries": [
                        {
                            "query": q.get("query_text", "—"),
                            "clicks": q.get("indicators", {}).get("CLICKS", 0),
                            "impressions": q.get("indicators", {}).get("SHOWS", 0),
                            "ctr": round(q.get("indicators", {}).get("CTR", 0) * 100, 2),
                            "position": round(q.get("indicators", {}).get("POSITION", 0), 1),
                        }
                        for q in queries
                    ]
                }
            return {"error": f"HTTP {r.status}"}


async def get_errors() -> dict:
    """Получить ошибки сайта."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE}/monitoring/states", headers=HEADERS) as r:
            if r.status == 200:
                data = await r.json()
                return {
                    "states": data.get("states", [])
                }
            return {"error": f"HTTP {r.status}"}
