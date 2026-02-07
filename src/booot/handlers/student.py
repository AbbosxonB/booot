from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booot.keyboards import STUDENT_MAIN, inline_subtopics
from booot.models import Subtopic
from booot.services.tickets import ensure_user, student_can_create_ticket, create_ticket, list_student_tickets

router = Router()


class TicketFlow(StatesGroup):
    choosing_subtopic = State()
    entering_comment = State()
    entering_subject = State()


FAQ_TEXT = (
    "📌 FAQ (qisqa):\n"
    "• IT muammolari bo‘lsa: avval login/parolni tekshiring, portalga qayta kiring.\n"
    "• To‘lov masalalari: kvitansiya/ID bo‘lsa yuboring.\n"
    "• Bahoga e’tiroz: fan, o‘qituvchi, sana va sababni yozing.\n"
)

@router.message(F.text == "📌 Ma’lumotlar (FAQ)")
async def faq(message: Message):
    await message.answer(FAQ_TEXT, reply_markup=STUDENT_MAIN)

@router.message(F.text == "👤 Profil")
async def profile(message: Message, session: AsyncSession):
    u = await ensure_user(session, message.from_user.id, message.from_user.full_name or "")
    await message.answer(
        f"👤 Profil:\n"
        f"Ism: {u.full_name}\n"
        f"Guruh: {u.group or 'kiritilmagan'}\n"
        f"Rol: {u.role}",
        reply_markup=STUDENT_MAIN,
    )

@router.message(F.text == "📄 Murojaatlarim")
async def my_tickets(message: Message, session: AsyncSession):
    u = await ensure_user(session, message.from_user.id, message.from_user.full_name or "")
    items = await list_student_tickets(session, u)
    if not items:
        await message.answer("Sizda hozircha murojaat yo‘q.", reply_markup=STUDENT_MAIN)
        return
    lines = []
    for t in items:
        lines.append(f"• {t.public_id} — {t.status} — {t.priority}")
    await message.answer("📄 Murojaatlaringiz:\n" + "\n".join(lines), reply_markup=STUDENT_MAIN)

@router.message(F.text == "📨 Murojaat yuborish")
async def create_ticket_start(message: Message, session: AsyncSession, state: FSMContext):
    u = await ensure_user(session, message.from_user.id, message.from_user.full_name or "")
    ok, remain = await student_can_create_ticket(session, u)
    if not ok:
        await message.answer(f"⏳ Siz yaqinda murojaat yuborgansiz. {remain} daqiqadan keyin urinib ko‘ring.")
        return

    # IT subtopic tanlashdan oldin FAQ ko‘rsatamiz (talabingiz)
    await message.answer("Eslatma: IT muammolari uchun avval FAQni tekshirib chiqing ✅\n\nSub-mavzuni tanlang:")

    subs = list((await session.execute(select(Subtopic.id, Subtopic.title))).all())
    await state.set_state(TicketFlow.choosing_subtopic)
    await message.answer("👇 Sub-mavzular:", reply_markup=inline_subtopics(subs))

@router.callback_query(F.data.startswith("subtopic:"))
async def subtopic_chosen(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    sub_id = int(cb.data.split(":")[1])
    sub = (await session.execute(select(Subtopic).where(Subtopic.id == sub_id))).scalar_one()

    await state.update_data(subtopic_id=sub_id, required_fields=sub.required_fields)

    # minimal fields
    fields = (sub.required_fields or "comment").split(",")
    if "subject" in fields:
        await state.set_state(TicketFlow.entering_subject)
        await cb.message.edit_text("Sarlavha (qisqa) kiriting:")
    else:
        await state.set_state(TicketFlow.entering_comment)
        if "comment_required" in fields:
            await cb.message.edit_text("Izoh majburiy. Muammoni batafsil yozing:")
        else:
            await cb.message.edit_text("Muammoni qisqa va aniq yozing:")

    await cb.answer()

@router.message(TicketFlow.entering_subject)
async def enter_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text.strip())
    await state.set_state(TicketFlow.entering_comment)
    await message.answer("Endi muammoni batafsil yozing:")

@router.message(TicketFlow.entering_comment)
async def enter_comment(message: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    comment = message.text.strip()

    required_fields = (data.get("required_fields") or "comment").split(",")
    if "comment_required" in required_fields and len(comment) < 5:
        await message.answer("Izoh majburiy. Iltimos, batafsilroq yozing.")
        return

    u = await ensure_user(session, message.from_user.id, message.from_user.full_name or "")
    payload = {
        "subject": data.get("subject", ""),
        "comment": comment,
    }

    t = await create_ticket(session, u, int(data["subtopic_id"]), payload)
    await state.clear()

    await message.answer(
        f"✅ Murojaatingiz qabul qilindi!\nTicket: {t.public_id}\nHolat: {t.status}\n\n"
        f"Javob bo‘lsa shu bot orqali ko‘rasiz.",
        reply_markup=STUDENT_MAIN,
    )
