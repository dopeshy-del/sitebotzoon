import aiohttp
from config import TIMEWEB_API_TOKEN, TIMEWEB_API_URL


HEADERS = {
    "Authorization": f"Bearer {TIMEWEB_API_TOKEN}",
    "Content-Type": "application/json",
}


async def get_account_balance() -> dict:
    """РџРѕР»СѓС‡РёС‚СЊ Р±Р°Р»Р°РЅСЃ Р°РєРєР°СѓРЅС‚Р° TimeWeb."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/account/finances", headers=HEADERS) as r:
            data = await r.json()
            finances = data.get("finances", {})
            return {
                "balance": finances.get("balance", 0),
                "currency": "в‚Ѕ",
                "bonus": finances.get("bonus_balance", 0),
            }


async def get_servers() -> list:
    """РџРѕР»СѓС‡РёС‚СЊ СЃРїРёСЃРѕРє VPS СЃРµСЂРІРµСЂРѕРІ."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/servers", headers=HEADERS) as r:
            data = await r.json()
            servers = data.get("servers", [])
            result = []
            for s in servers:
                result.append({
                    "id": s.get("id"),
                    "name": s.get("name", "вЂ”"),
                    "status": s.get("status", "unknown"),
                    "cpu": s.get("cpu", 0),
                    "ram": s.get("ram", 0),
                    "disk": s.get("hdd", 0),
                    "ip": s.get("networks", [{}])[0].get("ips", [{}])[0].get("ip", "вЂ”")
                            if s.get("networks") else "вЂ”",
                    "location": s.get("location", "вЂ”"),
                    "os": s.get("os", {}).get("name", "вЂ”"),
                })
            return result


async def get_server_stats(server_id: int) -> dict:
    """РџРѕР»СѓС‡РёС‚СЊ СЃС‚Р°С‚РёСЃС‚РёРєСѓ РєРѕРЅРєСЂРµС‚РЅРѕРіРѕ СЃРµСЂРІРµСЂР°."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{TIMEWEB_API_URL}/servers/{server_id}/statistics",
            headers=HEADERS
        ) as r:
            return await r.json()


async def reboot_server(server_id: int) -> bool:
    """РџРµСЂРµР·Р°РіСЂСѓР·РёС‚СЊ СЃРµСЂРІРµСЂ."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{TIMEWEB_API_URL}/servers/{server_id}/action",
            headers=HEADERS,
            json={"action": "reboot"}
        ) as r:
            return r.status == 200


async def get_domains() -> list:
    """РџРѕР»СѓС‡РёС‚СЊ СЃРїРёСЃРѕРє РґРѕРјРµРЅРѕРІ."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TIMEWEB_API_URL}/domains", headers=HEADERS) as r:
            data = await r.json()
            domains = data.get("domains", [])
            return [
                {
                    "fqdn": d.get("fqdn", "вЂ”"),
                    "status": d.get("status", "вЂ”"),
                    "expires": d.get("expiration", "вЂ”"),
                }
                for d in domains
            ]
