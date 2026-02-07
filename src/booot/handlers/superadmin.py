from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booot.config import settings
from booot.enums import Role
from booot.models import User, Department
from booot.services.tickets import ensure_user

router = Router()

def _is_superadmin(tg_id: int) -> bool:
    return tg_id in settings.superadmin_ids()

@router.message(F.text.startswith("/grant "))
async def grant_role(message: Message, session: AsyncSession):
    # /grant <tg_id> <ROLE>
    if not _is_superadmin(message.from_user.id):
        await message.answer("Faqat superadmin.")
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Format: /grant <tg_id> <STUDENT|STAFF|ADMIN|SUPERADMIN>")
        return
    tg_id = int(parts[1])
    role = parts[2].upper()
    u = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not u:
        u = await ensure_user(session, tg_id, "")
    u.role = role
    await session.commit()
    await message.answer(f"✅ Role berildi: {tg_id} -> {role}")

@router.message(F.text.startswith("/assign_dep "))
async def assign_dep(message: Message, session: AsyncSession):
    # /assign_dep <tg_id> <DEKANAT|OQUV|BUX|MKT|IT>
    if not _is_superadmin(message.from_user.id):
        await message.answer("Faqat superadmin.")
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Format: /assign_dep <tg_id> <DEKANAT|OQUV|BUX|MKT|IT>")
        return
    tg_id = int(parts[1])
    code = parts[2].upper()

    dep = (await session.execute(select(Department).where(Department.code == code))).scalar_one_or_none()
    if not dep:
        await message.answer("Bo‘lim topilmadi (seed ishlaganini tekshiring).")
        return
    u = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not u:
        await message.answer("User topilmadi. Avval user botga /start qilsin yoki /grant bilan yarating.")
        return
    u.department_id = dep.id
    if u.role == Role.STUDENT.value:
        u.role = Role.STAFF.value
    await session.commit()
    await message.answer(f"✅ Xodim bo‘limi biriktirildi: {tg_id} -> {code}")
