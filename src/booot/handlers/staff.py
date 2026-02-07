from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booot.config import settings
from booot.enums import Role
from booot.keyboards import inline_staff_menu, inline_ticket_actions
from booot.models import User, Ticket
from booot.permissions import has_role
from booot.services.tickets import ensure_user, staff_new_tickets, staff_unanswered_tickets, take_ticket, add_staff_reply, close_ticket

router = Router()


class StaffFlow(StatesGroup):
    replying = State()


def _is_superadmin(tg_id: int) -> bool:
    return tg_id in settings.superadmin_ids()


async def _load_user(session: AsyncSession, tg_id: int, full_name: str) -> User:
    u = await ensure_user(session, tg_id, full_name)
    # env superadmins override
    if _is_superadmin(tg_id) and u.role != Role.SUPERADMIN.value:
        u.role = Role.SUPERADMIN.value
        await session.commit()
    return u


@router.message(F.text.in_({"/panel", "🛠 Panel"}))
async def panel(message: Message, session: AsyncSession):
    u = await _load_user(session, message.from_user.id, message.from_user.full_name or "")
    if not has_role(u.role, {Role.STAFF, Role.ADMIN, Role.SUPERADMIN}):
        await message.answer("Sizda panelga ruxsat yo‘q.")
        return
    await message.answer("🛠 Xodim/Admin panel:", reply_markup=inline_staff_menu())


@router.callback_query(F.data == "staff:new")
async def staff_new(cb: CallbackQuery, session: AsyncSession):
    u = await _load_user(session, cb.from_user.id, cb.from_user.full_name or "")
    if not has_role(u.role, {Role.STAFF, Role.ADMIN, Role.SUPERADMIN}):
        await cb.answer("Ruxsat yo‘q", show_alert=True)
        return

    if u.role == Role.STAFF.value and not u.department_id:
        await cb.message.edit_text("Sizga bo‘lim biriktirilmagan (superadmin sozlashi kerak).")
        await cb.answer()
        return

    dep_id = u.department_id if u.role == Role.STAFF.value else (u.department_id or u.department_id or 0)
    # Admin/Superadmin: hozircha o‘z department_id bo‘lsa shuni; keyin “barcha”ni ham qo‘shamiz.
    if u.role in {Role.ADMIN.value, Role.SUPERADMIN.value} and dep_id == 0:
        await cb.message.edit_text("Admin uchun hozircha department_id kerak. (Keyingi qadam: global view).")
        await cb.answer()
        return

    tickets = await staff_new_tickets(session, dep_id)
    if not tickets:
        await cb.message.edit_text("Yangi murojaat yo‘q.")
        await cb.answer()
        return

    out = []
    for t in tickets:
        out.append(f"• {t.public_id} — {t.status} — {t.priority}")
    await cb.message.edit_text("📥 Yangi murojaatlar:\n" + "\n".join(out) + "\n\nTicket ID kiriting: /t <id>")
    await cb.answer()


@router.message(F.text.startswith("/t "))
async def open_ticket(message: Message, session: AsyncSession):
    u = await _load_user(session, message.from_user.id, message.from_user.full_name or "")
    if not has_role(u.role, {Role.STAFF, Role.ADMIN, Role.SUPERADMIN}):
        await message.answer("Ruxsat yo‘q.")
        return

    try:
        ticket_id = int(message.text.split(" ", 1)[1].strip())
    except Exception:
        await message.answer("Format: /t <ticket_db_id>")
        return

    t = (await session.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one_or_none()
    if not t:
        await message.answer("Ticket topilmadi.")
        return

    if u.role == Role.STAFF.value and u.department_id != t.department_id:
        await message.answer("Bu ticket sizning bo‘limingizga tegishli emas.")
        return

    can_transfer = u.role in {Role.ADMIN.value, Role.SUPERADMIN.value}
    await message.answer(
        f"🎟 {t.public_id}\nHolat: {t.status}\nPriority: {t.priority}\nStudent ID: {t.student_id}\n\n"
        f"Action tanlang:",
        reply_markup=inline_ticket_actions(t.id, can_transfer=can_transfer),
    )


@router.callback_query(F.data.startswith("t_take:"))
async def cb_take(cb: CallbackQuery, session: AsyncSession):
    u = await _load_user(session, cb.from_user.id, cb.from_user.full_name or "")
    if not has_role(u.role, {Role.STAFF, Role.ADMIN, Role.SUPERADMIN}):
        await cb.answer("Ruxsat yo‘q", show_alert=True)
        return
    ticket_id = int(cb.data.split(":")[1])
    t = await take_ticket(session, ticket_id, u)
    await cb.message.edit_text(f"✅ Ticket ishga olindi: {t.public_id} (IN_PROGRESS)")
    await cb.answer()


class ReplyFlow(StatesGroup):
    waiting_text = State()

@router.callback_query(F.data.startswith("t_reply:"))
async def cb_reply(cb: CallbackQuery, state: FSMContext):
    ticket_id = int(cb.data.split(":")[1])
    await state.set_state(ReplyFlow.waiting_text)
    await state.update_data(ticket_id=ticket_id)
    await cb.message.edit_text("✍️ Javob matnini yuboring:")
    await cb.answer()

@router.message(ReplyFlow.waiting_text)
async def do_reply(message: Message, session: AsyncSession, state: FSMContext):
    u = await _load_user(session, message.from_user.id, message.from_user.full_name or "")
    if not has_role(u.role, {Role.STAFF, Role.ADMIN, Role.SUPERADMIN}):
        await message.answer("Ruxsat yo‘q.")
        return
    data = await state.get_data()
    ticket_id = int(data["ticket_id"])
    t = await add_staff_reply(session, ticket_id, u, message.text.strip())
    await state.clear()
    await message.answer(f"✅ Javob saqlandi: {t.public_id} (ANSWERED)\nEndi ticketni yopish mumkin.")

@router.callback_query(F.data.startswith("t_close:"))
async def cb_close(cb: CallbackQuery, session: AsyncSession):
    u = await _load_user(session, cb.from_user.id, cb.from_user.full_name or "")
    if not has_role(u.role, {Role.STAFF, Role.ADMIN, Role.SUPERADMIN}):
        await cb.answer("Ruxsat yo‘q", show_alert=True)
        return
    ticket_id = int(cb.data.split(":")[1])
    try:
        t = await close_ticket(session, ticket_id)
    except ValueError as e:
        await cb.answer(str(e), show_alert=True)
        return
    await cb.message.edit_text(f"📄 Ticket yopildi: {t.public_id} (CLOSED)")
    await cb.answer()
