from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booot.config import settings
from booot.enums import TicketStatus
from booot.models import Ticket


async def tickets_needing_reminder(session: AsyncSession) -> list[Ticket]:
    # OPEN/IN_PROGRESS va created_at eski bo‘lsa reminder
    remind_at = datetime.utcnow() - timedelta(minutes=settings.remind_after_minutes)
    q = select(Ticket).where(
        Ticket.status.in_([TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value]),
        Ticket.created_at <= remind_at,
    )
    return list((await session.execute(q)).scalars().all())


async def tickets_needing_escalation(session: AsyncSession) -> list[Ticket]:
    esc_at = datetime.utcnow() - timedelta(minutes=settings.escalate_after_minutes)
    q = select(Ticket).where(
        Ticket.status.in_([TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value]),
        Ticket.created_at <= esc_at,
    )
    return list((await session.execute(q)).scalars().all())
