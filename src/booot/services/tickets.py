from __future__ import annotations

import json
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from booot.config import settings
from booot.enums import TicketStatus, Priority
from booot.models import User, Ticket, TicketMessage, Subtopic


def _make_public_id(seq: int) -> str:
    # oddiy, lekin unique: T-YYYY-000123
    year = datetime.utcnow().year
    return f"T-{year}-{seq:06d}"


async def ensure_user(session: AsyncSession, tg_id: int, full_name: str) -> User:
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    user = res.scalar_one_or_none()
    if user:
        if full_name and user.full_name != full_name:
            user.full_name = full_name
            await session.commit()
        return user
    user = User(tg_id=tg_id, full_name=full_name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def student_can_create_ticket(session: AsyncSession, student: User) -> tuple[bool, int]:
    cooldown = timedelta(minutes=settings.student_ticket_cooldown_minutes)
    since = datetime.utcnow() - cooldown

    q = select(func.count(Ticket.id)).where(
        Ticket.student_id == student.id,
        Ticket.created_at >= since,
    )
    count = (await session.execute(q)).scalar_one()
    if count >= 1:
        remaining = int((cooldown - (datetime.utcnow() - since)).total_seconds() // 60)
        return False, max(1, remaining)
    return True, 0


async def create_ticket(
    session: AsyncSession,
    student: User,
    subtopic_id: int,
    payload: dict,
) -> Ticket:
    sub = (await session.execute(select(Subtopic).where(Subtopic.id == subtopic_id))).scalar_one()

    # sequence from db count (simple). For production: use DB sequence.
    seq = (await session.execute(select(func.count(Ticket.id)))).scalar_one() + 1
    public_id = _make_public_id(seq)

    t = Ticket(
        public_id=public_id,
        student_id=student.id,
        subtopic_id=sub.id,
        department_id=sub.department_id,
        status=TicketStatus.OPEN.value,
        priority=sub.priority or Priority.NORMAL.value,
        payload_json=json.dumps(payload, ensure_ascii=False),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(t)
    await session.commit()
    await session.refresh(t)

    # store initial message as history
    msg = TicketMessage(ticket_id=t.id, author_user_id=student.id, text=payload.get("comment", ""))
    session.add(msg)
    await session.commit()
    return t


async def list_student_tickets(session: AsyncSession, student: User, limit: int = 10) -> list[Ticket]:
    q = (
        select(Ticket)
        .where(Ticket.student_id == student.id)
        .order_by(desc(Ticket.created_at))
        .limit(limit)
    )
    return list((await session.execute(q)).scalars().all())


async def staff_new_tickets(session: AsyncSession, department_id: int, limit: int = 10) -> list[Ticket]:
    q = (
        select(Ticket)
        .where(Ticket.department_id == department_id, Ticket.status == TicketStatus.OPEN.value)
        .order_by(desc(Ticket.priority), desc(Ticket.created_at))
        .limit(limit)
    )
    return list((await session.execute(q)).scalars().all())


async def staff_unanswered_tickets(session: AsyncSession, department_id: int, limit: int = 10) -> list[Ticket]:
    q = (
        select(Ticket)
        .where(
            Ticket.department_id == department_id,
            Ticket.status.in_([TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value]),
        )
        .order_by(desc(Ticket.created_at))
        .limit(limit)
    )
    return list((await session.execute(q)).scalars().all())


async def take_ticket(session: AsyncSession, ticket_id: int, staff: User) -> Ticket:
    t = (await session.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one()
    t.assigned_staff_id = staff.id
    t.status = TicketStatus.IN_PROGRESS.value
    t.updated_at = datetime.utcnow()
    await session.commit()
    return t


async def add_staff_reply(session: AsyncSession, ticket_id: int, staff: User, text: str) -> Ticket:
    t = (await session.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one()
    session.add(TicketMessage(ticket_id=ticket_id, author_user_id=staff.id, text=text))
    t.status = TicketStatus.ANSWERED.value
    t.last_staff_reply_at = datetime.utcnow()
    t.updated_at = datetime.utcnow()
    await session.commit()
    return t


async def close_ticket(session: AsyncSession, ticket_id: int) -> Ticket:
    t = (await session.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one()
    if t.status != TicketStatus.ANSWERED.value:
        # "Ticket javobsiz yopilmaydi"
        raise ValueError("Ticket javobsiz yopilmaydi")
    t.status = TicketStatus.CLOSED.value
    t.updated_at = datetime.utcnow()
    await session.commit()
    return t
