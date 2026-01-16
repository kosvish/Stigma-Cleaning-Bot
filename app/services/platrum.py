import aiohttp
import time
from typing import List, Dict, Optional

from app.services.users_service import get_user_by_id

# Настройки (лучше вынести в config.py, но для примера оставлю тут)
PLATRUM_URL = "https://9c3e4fb.platrum.ru"  # Твой домен
API_KEY = "C350AE11-C3E4-F97EA3B694CE5C4CAD9A378BF6"  # Вставь свой ключ!
HEADERS = {
    'Content-type': 'application/json',
    'Api-key': API_KEY
}

# Глобальный кэш
_categories_cache: List[Dict] = []
_last_fetch_time = 0
CACHE_TTL = 600  # Кэш живет 10 минут
_cashboxes_cache: List[Dict] = []
_cashboxes_last_fetch = 0


async def get_raw_categories() -> List[Dict]:
    """Загружает все категории из Platrum с кэшированием."""
    global _categories_cache, _last_fetch_time

    if time.time() - _last_fetch_time < CACHE_TTL and _categories_cache:
        return _categories_cache

    url = f"{PLATRUM_URL}/fintransaction/api/category/list"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('status') == 'success':
                        _categories_cache = data.get('data', [])
                        _last_fetch_time = time.time()
                        return _categories_cache
    except Exception as e:
        print(f"❌ Ошибка API Platrum: {e}")

    return []


async def get_platrum_expense_categories(parent_id: Optional[int] = None) -> List[Dict]:
    """
    Возвращает отфильтрованный список категорий (только расходы).
    parent_id=None -> Главные категории.
    parent_id=123 -> Подкатегории для 123.
    """
    all_cats = await get_raw_categories()
    filtered = []

    for cat in all_cats:
        # 1. Только расходы (out)
        # 2. Не архивные
        # 3. Совпадение по родителю
        if (cat.get('transaction_type') == 'out' and
                not cat.get('is_archived') and
                cat.get('parent_id') == parent_id):
            filtered.append(cat)

    return filtered


async def get_platrum_category_name(category_id: int) -> str:
    """Ищет имя категории по ID в кэше."""
    all_cats = await get_raw_categories()
    for cat in all_cats:
        if cat['id'] == category_id:
            return cat['name']
    return "Неизвестно"


async def get_platrum_cashboxes() -> List[Dict]:
    """
    Получает список касс (cashboxes) из Platrum.
    Возвращает только НЕ архивные кассы.
    """
    global _cashboxes_cache, _cashboxes_last_fetch

    # Кэш на 10 минут
    if time.time() - _cashboxes_last_fetch < 600 and _cashboxes_cache:
        return _cashboxes_cache

    url = f"{PLATRUM_URL}/finance/api/transaction/cashbox-list"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('status') == 'success':
                        all_cashboxes = data.get('data', [])

                        # Фильтруем: берем только те, где is_archived равно null или false
                        # (в python null это None)
                        active_cashboxes = [
                            cb for cb in all_cashboxes
                            if not cb.get('is_archived')
                        ]

                        _cashboxes_cache = active_cashboxes
                        _cashboxes_last_fetch = time.time()
                        return _cashboxes_cache
    except Exception as e:
        print(f"❌ Ошибка API Platrum (Cashboxes): {e}")

    return []


async def get_platrum_cashbox_name(cashbox_id: int) -> str:
    """Ищет имя кассы по ID в кэше."""
    cashboxes = await get_platrum_cashboxes()
    for cb in cashboxes:
        if cb['id'] == cashbox_id:
            return cb['name']
    return "Неизвестно"


async def create_platrum_expense(data: dict, telegram_user_id: int) -> bool:
    """
    Создает транзакцию расхода в Platrum, используя platrum_id из базы данных.
    """
    url = f"{PLATRUM_URL}/fintransaction/api/transaction/create"

    # 1. Получаем пользователя из БД по Telegram ID
    user = get_user_by_id(telegram_user_id)

    # Проверяем, есть ли пользователь и заполнен ли у него platrum_id
    if not user:
        print(f"❌ Ошибка Platrum: Пользователь с Telegram ID {telegram_user_id} не найден в базе бота.")
        return False

    if not user.platrum_id:
        platrum_user_id = ''
    else:
        platrum_user_id = str(user.platrum_id)

    # 2. Определяем категорию
    # Если выбрана подкатегория (не 0) - берем её. Иначе берем родительскую категорию.
    final_category_id = int(data.get('subcategory_id', 0))
    if final_category_id == 0:
        final_category_id = int(data.get('category_id'))

    # 3. Формируем JSON
    try:
        amount = int(float(data.get('cost')))  # Platrum просит int
    except:
        amount = 0

    payload = {
        "type": "out",  # Расход
        "sum": amount,
        "cashbox_id": int(data.get('cashbox_id')),
        "category_id": final_category_id,
        "description": data.get('name', 'Расход из Telegram бота'),
        "user_id": platrum_user_id,  # <-- Берем из БД

        # Дополнительные поля, если нужны
        # "project_id": ...
    }

    # 4. Отправляем запрос
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=HEADERS, json=payload) as resp:
                response_data = await resp.json()

                # Логируем ответ для отладки
                print(f"📤 Platrum Response: {resp.status} - {response_data}")

                if resp.status == 200 and response_data.get('status') == 'success':
                    return True
                else:
                    print(f"❌ Ошибка создания транзакции в Platrum: {response_data}")
                    return False
    except Exception as e:
        print(f"❌ Ошибка соединения с Platrum: {e}")
        return False
