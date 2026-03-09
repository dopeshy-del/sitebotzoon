import aiohttp
from typing import Any

from config import CURSOR_API_KEY, CURSOR_API_URL


HEADERS = {
    "Authorization": f"Bearer {CURSOR_API_KEY}",
    "Content-Type": "application/json",
}


BASE_URLS = [CURSOR_API_URL.rstrip("/")]
if "api.cursor.com" not in CURSOR_API_URL:
    BASE_URLS.append("https://api.cursor.com/v1")


async def get_limits() -> dict:
    """Best-effort получение лимитов/usage Cursor API через известные endpoint-кандидаты."""
    endpoint_candidates = (
        "/usage",
        "/usage/summary",
        "/billing/usage",
        "/billing/limits",
        "/limits",
    )

    async with aiohttp.ClientSession() as session:
        for base_url in BASE_URLS:
            for endpoint in endpoint_candidates:
                try:
                    async with session.get(f"{base_url}{endpoint}", headers=HEADERS) as r:
                        if r.status != 200:
                            continue
                        payload = await r.json()
                        parsed = _parse_limits_payload(payload)
                        if parsed:
                            parsed["source_endpoint"] = endpoint
                            return parsed
                except (aiohttp.ClientError, ValueError, TypeError):
                    continue

    return {"error": "Не удалось получить лимиты Cursor", "remaining": None}


async def get_recent_runs(limit: int = 20) -> dict:
    """Best-effort получение последних задач/генераций Cursor."""
    endpoint_candidates = (
        f"/runs?limit={limit}",
        f"/tasks?limit={limit}",
        f"/generations?limit={limit}",
        f"/jobs?limit={limit}",
    )

    async with aiohttp.ClientSession() as session:
        for base_url in BASE_URLS:
            for endpoint in endpoint_candidates:
                try:
                    async with session.get(f"{base_url}{endpoint}", headers=HEADERS) as r:
                        if r.status != 200:
                            continue
                        payload = await r.json()
                        runs = _extract_runs(payload)
                        if runs:
                            return {
                                "runs": runs,
                                "source_endpoint": endpoint,
                            }
                except (aiohttp.ClientError, ValueError, TypeError):
                    continue

    return {"runs": [], "error": "Не удалось получить список задач Cursor"}


def _parse_limits_payload(payload: dict[str, Any]) -> dict:
    remaining = _first_number(payload, ("remaining", "credits_remaining", "quota_remaining", "left"))
    used = _first_number(payload, ("used", "credits_used", "quota_used", "spent"), default=0.0)
    total = _first_number(payload, ("total", "limit", "credits_total", "quota_total"), default=0.0)

    if isinstance(payload.get("limits"), dict):
        data = payload["limits"]
        remaining = remaining if remaining is not None else _first_number(data, ("remaining", "left"))
        used = max(used, _first_number(data, ("used",), default=0.0))
        total = max(total, _first_number(data, ("total", "limit"), default=0.0))

    if remaining is None and total > 0:
        remaining = max(total - used, 0)

    if remaining is None and total == 0 and used == 0:
        return {}

    return {
        "remaining": round(float(remaining), 4) if remaining is not None else None,
        "used": round(float(used), 4),
        "total": round(float(total), 4),
    }


def _extract_runs(payload: Any) -> list[dict]:
    items = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("runs", "tasks", "generations", "jobs", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                items = value
                break

    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        run_id = str(item.get("id") or item.get("run_id") or item.get("task_id") or "")
        status = str(item.get("status") or item.get("state") or "unknown").lower()
        prompt = (
            item.get("prompt")
            or item.get("input")
            or item.get("title")
            or item.get("name")
            or "—"
        )
        finished_at = (
            item.get("finished_at")
            or item.get("completed_at")
            or item.get("updated_at")
            or item.get("ended_at")
            or ""
        )
        if not run_id:
            continue
        out.append(
            {
                "id": run_id,
                "status": status,
                "prompt": str(prompt)[:140],
                "finished_at": str(finished_at),
            }
        )
    return out


def _first_number(data: dict[str, Any], keys: tuple[str, ...], default: float | None = None) -> float | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return default
