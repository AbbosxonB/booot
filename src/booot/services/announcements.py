from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from booot.models import Announcement


async def list_announcements(session: AsyncSession, limit: int = 5) -> list[Announcement]:
    q = select(Announcement).order_by(desc(Announcement.created_at)).limit(limit)
    return list((await session.execute(q)).scalars().all())


async def create_announcement(session: AsyncSession, title: str, body: str) -> Announcement:
    a = Announcement(title=title, body=body)
    session.add(a)
    await session.commit()
    await session.refresh(a)
    return a
