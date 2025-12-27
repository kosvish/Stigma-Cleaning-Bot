import requests
from datetime import datetime
import pytz

from app.config import WEBAPP_URL

GOOGLE_EXPENSES_URL = "https://script.google.com/macros/s/AKfycbzCNOMJiidv3WW_Tz-8iyXyfI4rfMAn4mSnMesKiV5o4-5oRhWfzKsQUsBjk2GsHxJugA/exec"


def append_expense_to_sheet(data: dict) -> bool:
    """
    Отправляет расход в Google Sheets через GAS
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
    }

    try:
        resp = requests.post(
            GOOGLE_EXPENSES_URL,
            json=payload,
            timeout=10
        )

        if resp.status_code == 200:
            result = resp.json()
            return result.get("status") == "ok"

    except Exception as e:
        print("❌ Ошибка отправки в Google Sheets:", e)

    return False


def get_recent_order_ids(days: int = 3) -> list[str]:
    try:
        resp = requests.get(WEBAPP_URL, params={"action": "recent_orders", "days": days})
        print(resp.text)
        if resp.status_code == 200:
            return resp.json()  # Список ID заказов
    except Exception as e:
        print("Ошибка при запросе заказов:", e)
    return []