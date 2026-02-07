from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booot.enums import Priority
from booot.models import Department, Subtopic
from booot.services.routing import DEPARTMENTS, SUBTOPICS


async def seed_if_needed(session: AsyncSession) -> None:
    # departments
    for code, name in DEPARTMENTS:
        exists = (await session.execute(select(Department).where(Department.code == code))).scalar_one_or_none()
        if not exists:
            session.add(Department(code=code, name=name))
    await session.commit()

    # subtopics
    dep_map = {d.code: d for d in (await session.execute(select(Department))).scalars().all()}

    for code, title, dep_code, prio, fields in SUBTOPICS:
        exists = (await session.execute(select(Subtopic).where(Subtopic.code == code))).scalar_one_or_none()
        if exists:
            continue
        dep = dep_map[dep_code]
        session.add(
            Subtopic(
                code=code,
                title=title,
                department_id=dep.id,
                priority=(prio.value if hasattr(prio, "value") else str(prio)),
                required_fields=fields,
            )
        )
    await session.commit()
