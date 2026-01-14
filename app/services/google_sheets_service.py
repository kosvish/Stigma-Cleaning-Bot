import aiohttp


GOOGLE_EXPENSES_URL = "https://script.google.com/macros/s/AKfycbyDhS0ltUhQGZuVDihUgtj9M331WYW91GPHqTLO-B1pBke0I3jYy1U4JDIitTwr8nyEeA/exec"


async def append_expense_to_sheet(data: dict) -> bool:
    """
    Отправляет расход в Google Sheets (Асинхронно)
    """
    payload = {
        "date": data.get("date"),
        "type": data.get("expense_value"),
        "category": data.get("category"),
        "subcategory": data.get("subcategory"),
        "brand": data.get("brand"),
        "qty": data.get("quantity"),
        "title": data.get("name"),
        "amount": data.get("cost"),
        "order_id": data.get("order_id") or "",
        "city": data.get("city"),
        "image_base64": data.get("image_base64"),
        "image_name": data.get("image_name")
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GOOGLE_EXPENSES_URL, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("status") == "ok"
    except Exception as e:
        print("❌ Ошибка отправки в Google Sheets:", e)

    return False


async def get_recent_order_ids(days: int = 3) -> list[str]:
    """
    Получает заказы (Асинхронно)
    """
    try:
        params = {"action": "recent_orders", "days": days}
        async with aiohttp.ClientSession() as session:
            # Таймаут чуть больше, на случай если Google тупит
            async with session.get(GOOGLE_EXPENSES_URL, params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
    except Exception as e:
        print("Ошибка при запросе заказов:", e)
    return []