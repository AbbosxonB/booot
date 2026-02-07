from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

STUDENT_MAIN = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📌 Ma’lumotlar (FAQ)")],
        [KeyboardButton(text="📨 Murojaat yuborish")],
        [KeyboardButton(text="📄 Murojaatlarim")],
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="📢 E’lonlar")],
    ],
    resize_keyboard=True,
)

def inline_subtopics(options: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for sid, title in options:
        kb.button(text=title, callback_data=f"subtopic:{sid}")
    kb.adjust(1)
    return kb.as_markup()

def inline_ticket_actions(ticket_id: int, can_transfer: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Ishga oldim", callback_data=f"t_take:{ticket_id}")
    kb.button(text="✍️ Javob yozish", callback_data=f"t_reply:{ticket_id}")
    if can_transfer:
        kb.button(text="🔁 O‘tkazish", callback_data=f"t_transfer:{ticket_id}")
    kb.button(text="📄 Yopish", callback_data=f"t_close:{ticket_id}")
    kb.adjust(2, 2)
    return kb.as_markup()

def inline_staff_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📥 Yangi murojaatlar", callback_data="staff:new")
    kb.button(text="🕒 Javobsiz murojaatlar", callback_data="staff:unanswered")
    kb.button(text="📊 Statistika", callback_data="staff:stats")
    kb.adjust(1)
    return kb.as_markup()
