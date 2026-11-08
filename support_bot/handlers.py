import json
from aiogram import types
from config import ADMIN_IDS
from database import save_request

with open("faq.json", "r", encoding="utf-8") as f:
    FAQ = json.load(f)

def find_faq_answer(text: str) -> str | None:
    t = text.lower().replace("?", "").replace("!", "").strip()
    for item in FAQ:
        if item["question"] in t:
            return item["answer"]
    return None

def route_category(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["сайт", "ошибка", "оплата", "не работает", "не грузится", "аккаунт"]):
        return "programmers"
    if any(k in t for k in ["заказ", "товар", "доставка", "возврат", "обмен", "поврежден", "статус"]):
        return "sales"
    return "unknown"

async def handle_message(message: types.Message):
    text = message.text or ""
    answer = find_faq_answer(text)
    if answer:
        await message.answer(answer)
        return

    category = route_category(text)
    if category == "programmers":
        resp = "Проблема с сайтом или оплатой. Передаю запрос в отдел программистов."
    elif category == "sales":
        resp = "Вопрос по заказу или товару. Передаю запрос в отдел продаж."
    else:
        resp = "Не удалось определить категорию. Опишите проблему кратко — мы поможем."

    req_id = save_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        text=text,
        category=category
    )
    await message.answer(f"{resp}\nВаш запрос принят. Номер заявки: #{req_id}. Ответим в течение 24 часов.")

    # Уведомление админам
    for admin_id in ADMIN_IDS:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Взять в работу", callback_data=f"take_{req_id}")],
            [types.InlineKeyboardButton(text="Завершить", callback_data=f"done_{req_id}")]
        ])
        await message.bot.send_message(
            chat_id=admin_id,
            text=f"Новая заявка #{req_id}\nКатегория: {category}\nПользователь: {message.from_user.full_name} (@{message.from_user.username or 'нет'})\nТекст: {text}",
            reply_markup=kb
        )

async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    if data.startswith("take_"):
        req_id = int(data.split("_"))[1]
        from database import update_request_status
        update_request_status(req_id, "in_progress", assigned_to=callback.from_user.username)
        await callback.answer("Заявка взята в работу")
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ Статус: в работе (взял {callback.from_user.username})")
    elif data.startswith("done_"):
        req_id = int(data.split("_"))[1]
        from database import update_request_status
        update_request_status(req_id, "completed")
        await callback.answer("Заявка завершена")
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ Статус: завершено")
