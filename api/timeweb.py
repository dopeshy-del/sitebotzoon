import aiohttp
from config import TIMEWEB_API_TOKEN, TIMEWEB_API_URL


HEADERS = {
    "Authorization": f"Bearer {TIMEWEB_API_TOKEN}",
    "Content-Type": "application/json",
}


async def get_account_balance() -> dict:
    """Получить баланс аккаунта TimeWeb."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/account/finances", headers=HEADERS) as r:
            data = await r.json()
            finances = data.get("finances", {})
            return {
                "balance": finances.get("balance", 0),
                "currency": "₽",
                "bonus": finances.get("bonus_balance", 0),
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
