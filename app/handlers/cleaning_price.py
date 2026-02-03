from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.utils.callbacks import CalcCallback


router = Router()

# === КОНФИГУРАЦИЯ ЦЕН ===
PRICES = {
    'kitchen': {
        'size': {'small': 1500, 'std': 2500, 'large': 3500},
        'dirt': {'light': 1000, 'medium': 2000, 'heavy': 3000},
        'addons': {'micro': 500, 'oven': 800, 'fridge': 1000, 'kitchen_set': 600}
    },
    'bath': {
        'size': {'small': 2000, 'medium': 3000, 'large': 3500},
        'dirt': {'light': 500, 'medium': 1500, 'heavy': 2500}
    },
    'room': {
        'size': {'small': 2000, 'medium': 3000, 'large': 3800}
    },
    'window': 250,
    'hall': {'std': 600, 'large': 800},
    'cupboard': 500
}



class CalcState(StatesGroup):
    active = State()


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def get_cart_total(data: dict) -> int:

    total = 0

    # Кухня
    k = data.get('kitchen', {})
    if k:
        total += PRICES['kitchen']['size'].get(k.get('size'), 0)
        total += PRICES['kitchen']['dirt'].get(k.get('dirt'), 0)

        for addon in k.get('addons', []):
            base_price = PRICES['kitchen']['addons'].get(addon, 0)
            # Если выбрано сильное загрязнение допов (+20%)
            if k.get('addon_heavy', False):
                base_price *= 1.2
            total += base_price


    b = data.get('bath', {})
    if b:
        total += PRICES['bath']['size'].get(b.get('size'), 0)
        total += PRICES['bath']['dirt'].get(b.get('dirt'), 0)

    # Комнаты (список)
    rooms = data.get('rooms', [])
    for r in rooms:
        total += PRICES['room']['size'].get(r, 0)


    if data.get('cupboards'):

        total += len(rooms) * PRICES['cupboard']


    total += data.get('windows', 0) * PRICES['window']


    h = data.get('hall')
    if h:
        total += PRICES['hall'].get(h, 0)

    return int(total)


# === КЛАВИАТУРЫ ===

def kb_main_menu(total: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽 Кухня", callback_data=CalcCallback(action="menu", value="kitchen").pack()),
            InlineKeyboardButton(text="🛁 Ванная", callback_data=CalcCallback(action="menu", value="bath").pack())
        ],
        [
            InlineKeyboardButton(text="🛏 Комната (+)", callback_data=CalcCallback(action="room_add").pack()),
            InlineKeyboardButton(text="🪟 Окна (+1)", callback_data=CalcCallback(action="window_add").pack())
        ],
        [
            InlineKeyboardButton(text="🚪 Коридор", callback_data=CalcCallback(action="menu", value="hall").pack())
        ],
        [
            InlineKeyboardButton(text="🔄 Сброс", callback_data=CalcCallback(action="reset").pack()),
            InlineKeyboardButton(text=f"✅ ИТОГО: {total} ₽", callback_data=CalcCallback(action="finish").pack())
        ]
    ])


def kb_kitchen(data: dict):
    k = data.get('kitchen', {})
    addons = k.get('addons', [])
    heavy_addon = k.get('addon_heavy', False)

    def check(val, current): return "✅" if val == current else ""

    def check_list(val, lst): return "✅" if val in lst else ""

    kb = [
        # Размер
        [
            InlineKeyboardButton(text=f"{check('small', k.get('size'))} Мал (<10м²)",
                                 callback_data=CalcCallback(action="k_size", value="small").pack()),
            InlineKeyboardButton(text=f"{check('std', k.get('size'))} Стандарт",
                                 callback_data=CalcCallback(action="k_size", value="std").pack()),
            InlineKeyboardButton(text=f"{check('large', k.get('size'))} Бол (>15м²)",
                                 callback_data=CalcCallback(action="k_size", value="large").pack()),
        ],
        # Грязь
        [
            InlineKeyboardButton(text=f"{check('light', k.get('dirt'))} Грязь: Слабая",
                                 callback_data=CalcCallback(action="k_dirt", value="light").pack()),
            InlineKeyboardButton(text=f"{check('medium', k.get('dirt'))} Средняя",
                                 callback_data=CalcCallback(action="k_dirt", value="medium").pack()),
            InlineKeyboardButton(text=f"{check('heavy', k.get('dirt'))} Сильная",
                                 callback_data=CalcCallback(action="k_dirt", value="heavy").pack()),
        ],
        # Допы
        [InlineKeyboardButton(text="🔻 Дополнительно внутри: 🔻", callback_data="ignore")],
        [
            InlineKeyboardButton(text=f"{check_list('micro', addons)} СВЧ (+500)",
                                 callback_data=CalcCallback(action="k_addon", value="micro").pack()),
            InlineKeyboardButton(text=f"{check_list('oven', addons)} Духовка (+800)",
                                 callback_data=CalcCallback(action="k_addon", value="oven").pack()),
        ],
        [
            InlineKeyboardButton(text=f"{check_list('fridge', addons)} Холод (+1000)",
                                 callback_data=CalcCallback(action="k_addon", value="fridge").pack()),
            InlineKeyboardButton(text=f"{check_list('kitchen_set', addons)} Гарнитур (+600)",
                                 callback_data=CalcCallback(action="k_addon", value="kitchen_set").pack()),
        ],
        [
            InlineKeyboardButton(text=f"{'✅' if heavy_addon else '⬜️'} Сильное загрязнение допов (+20%)",
                                 callback_data=CalcCallback(action="k_addon_heavy").pack())
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=CalcCallback(action="back").pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def kb_bath(data: dict):
    b = data.get('bath', {})

    def check(val, current): return "✅" if val == current else ""

    kb = [
        [InlineKeyboardButton(text="Размер:", callback_data="ignore")],
        [
            InlineKeyboardButton(text=f"{check('small', b.get('size'))} <4м²",
                                 callback_data=CalcCallback(action="b_size", value="small").pack()),
            InlineKeyboardButton(text=f"{check('medium', b.get('size'))} 4-6м²",
                                 callback_data=CalcCallback(action="b_size", value="medium").pack()),
            InlineKeyboardButton(text=f"{check('large', b.get('size'))} >6м²",
                                 callback_data=CalcCallback(action="b_size", value="large").pack()),
        ],
        [InlineKeyboardButton(text="Загрязнение:", callback_data="ignore")],
        [
            InlineKeyboardButton(text=f"{check('light', b.get('dirt'))} Слабое",
                                 callback_data=CalcCallback(action="b_dirt", value="light").pack()),
            InlineKeyboardButton(text=f"{check('medium', b.get('dirt'))} Среднее",
                                 callback_data=CalcCallback(action="b_dirt", value="medium").pack()),
            InlineKeyboardButton(text=f"{check('heavy', b.get('dirt'))} Сильное",
                                 callback_data=CalcCallback(action="b_dirt", value="heavy").pack()),
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=CalcCallback(action="back").pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def kb_room_select():

    kb = [
        [InlineKeyboardButton(text="8-11 м² (2000₽)",
                              callback_data=CalcCallback(action="room_save", value="small").pack())],
        [InlineKeyboardButton(text="12-17 м² (3000₽)",
                              callback_data=CalcCallback(action="room_save", value="medium").pack())],
        [InlineKeyboardButton(text="18-25 м² (3800₽)",
                              callback_data=CalcCallback(action="room_save", value="large").pack())],
        [InlineKeyboardButton(text="🔙 Отмена", callback_data=CalcCallback(action="back").pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)




@router.callback_query(CalcCallback.filter(F.action == "start"))
async def start_calc(call: CallbackQuery, state: FSMContext):
    await state.set_state(CalcState.active)
    await state.set_data({})  # Очищаем корзину
    await call.message.edit_text("🧽 Калькулятор уборки\nВыберите зоны:", reply_markup=kb_main_menu(0), parse_mode="Markdown")


@router.callback_query(CalcCallback.filter(F.action == "back"))
async def back_to_main(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total = get_cart_total(data)


    summary = []
    if data.get('kitchen'): summary.append("🍽 Кухня")
    if data.get('bath'): summary.append("🛁 Ванная")
    if data.get('rooms'): summary.append(f"🛏 Комнат: {len(data['rooms'])}")
    if data.get('windows'): summary.append(f"🪟 Окон: {data['windows']}")

    text = "🧽 Калькулятор уборки\n"
    if summary:
        text += "В корзине: " + ", ".join(summary)

    await call.message.edit_text(text, reply_markup=kb_main_menu(total))


@router.callback_query(CalcCallback.filter(F.action == "reset"))
async def reset_calc(call: CallbackQuery, state: FSMContext):
    await state.set_data({})
    await call.message.edit_text("🔄 Расчет сброшен.\nВыберите зоны:", reply_markup=kb_main_menu(0))



@router.callback_query(CalcCallback.filter(F.action == "menu"), F.data.contains("kitchen"))
async def menu_kitchen(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'kitchen' not in data:
        data['kitchen'] = {'size': 'std', 'dirt': 'light', 'addons': []}
        await state.update_data(data)

    await call.message.edit_text("🍽 Настройка кухни:", reply_markup=kb_kitchen(data))


@router.callback_query(CalcCallback.filter(F.action.in_({"k_size", "k_dirt"})))
async def update_kitchen_main(call: CallbackQuery, callback_data: CalcCallback, state: FSMContext):
    data = await state.get_data()
    key = "size" if callback_data.action == "k_size" else "dirt"
    data['kitchen'][key] = callback_data.value
    await state.update_data(data)
    await call.message.edit_reply_markup(reply_markup=kb_kitchen(data))


@router.callback_query(CalcCallback.filter(F.action == "k_addon"))
async def toggle_k_addon(call: CallbackQuery, callback_data: CalcCallback, state: FSMContext):
    data = await state.get_data()
    addons = data['kitchen'].get('addons', [])
    val = callback_data.value

    if val in addons:
        addons.remove(val)
    else:
        addons.append(val)

    data['kitchen']['addons'] = addons
    await state.update_data(data)
    await call.message.edit_reply_markup(reply_markup=kb_kitchen(data))


@router.callback_query(CalcCallback.filter(F.action == "k_addon_heavy"))
async def toggle_k_heavy(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data['kitchen'].get('addon_heavy', False)
    data['kitchen']['addon_heavy'] = not current
    await state.update_data(data)
    await call.message.edit_reply_markup(reply_markup=kb_kitchen(data))



@router.callback_query(CalcCallback.filter(F.action == "menu"), F.data.contains("bath"))
async def menu_bath(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'bath' not in data:
        data['bath'] = {'size': 'small', 'dirt': 'light'}
        await state.update_data(data)
    await call.message.edit_text("🛁 Настройка ванной:", reply_markup=kb_bath(data))


@router.callback_query(CalcCallback.filter(F.action.in_({"b_size", "b_dirt"})))
async def update_bath(call: CallbackQuery, callback_data: CalcCallback, state: FSMContext):
    data = await state.get_data()
    key = "size" if callback_data.action == "b_size" else "dirt"
    data['bath'][key] = callback_data.value
    await state.update_data(data)
    await call.message.edit_reply_markup(reply_markup=kb_bath(data))



@router.callback_query(CalcCallback.filter(F.action == "room_add"))
async def room_add_menu(call: CallbackQuery):
    await call.message.edit_text("🛏 Выберите размер комнаты для добавления:", reply_markup=kb_room_select())


@router.callback_query(CalcCallback.filter(F.action == "room_save"))
async def room_save(call: CallbackQuery, callback_data: CalcCallback, state: FSMContext):
    data = await state.get_data()
    rooms = data.get('rooms', [])
    rooms.append(callback_data.value)
    data['rooms'] = rooms
    await state.update_data(data)


    total = get_cart_total(data)
    await call.message.edit_text(f"✅ Комната добавлена.\nВсего комнат: {len(rooms)}", reply_markup=kb_main_menu(total))



@router.callback_query(CalcCallback.filter(F.action == "window_add"))
async def window_add(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data.get('windows', 0)
    data['windows'] = current + 1
    await state.update_data(data)

    total = get_cart_total(data)
    try:
        await call.message.edit_reply_markup(reply_markup=kb_main_menu(total))
    except:
        pass



@router.callback_query(CalcCallback.filter(F.action == "menu"), F.data.contains("hall"))
async def toggle_hall(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data.get('hall')

    if current is None:
        new_val = 'std'
    elif current == 'std':
        new_val = 'large'
    else:
        new_val = None

    data['hall'] = new_val
    await state.update_data(data)

    state_text = "Нет"
    if new_val == 'std': state_text = "Стандарт (600р)"
    if new_val == 'large': state_text = "Большой (800р)"

    total = get_cart_total(data)
    await call.message.edit_text(f"🚪 Коридор: {state_text}\nВыберите зоны:", reply_markup=kb_main_menu(total))



@router.callback_query(CalcCallback.filter(F.action == "finish"))
async def finish_calc(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total = get_cart_total(data)

    text = f"✅ Итоговая стоимость: {total} ₽\n\n"
    if data.get('kitchen'): text += "- Кухня учтена\n"
    if data.get('bath'): text += "- Ванная учтена\n"
    if data.get('rooms'): text += f"- Комнаты: {len(data['rooms'])} шт\n"
    if data.get('windows'): text += f"- Окна: {data['windows']} шт\n"

    await call.message.edit_text(text, reply_markup=None)
    # await state.clear() # Можно очистить, а можно оставить, чтобы юзер мог вернуться и поправить