def format_expense_preview(data: dict) -> str:
    return (
        "🧾 <b>Проверьте данные расхода</b>\n\n"
        f"📅 Дата: <b>{data['date']}</b>\n"
        f"📌 Тип: <b>{data['type']}</b>\n"
        f"🏷 Категория: <b>{data['category_name']}</b>\n"
        f"📁 Подкатегория: <b>{data['subcategory_name']}</b>\n"
        f"🏭 Бренд: <b>{data.get('brand_name', '—')}</b>\n"
        f"🔢 Кол-во: <b>{data['qty']}</b>\n"
        f"📝 Назначение: <b>{data['title']}</b>\n"
        f"💰 Стоимость: <b>{data['price']}</b>\n"
        f"🔗 ID заказа: <b>{data.get('order_id', '—')}</b>\n"
        f"🏙 Город: <b>{data['city_name']}</b>\n"
    )
