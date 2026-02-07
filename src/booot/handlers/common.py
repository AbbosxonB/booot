from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from booot.keyboards import STUDENT_MAIN
from booot.services.tickets import ensure_user

router = Router()

@router.message(F.text == "/start")
async def start(message: Message, session: AsyncSession):
    user = await ensure_user(session, message.from_user.id, message.from_user.full_name or "")
    await message.answer(
        "Assalomu alaykum! Universitet Service Desk botiga xush kelibsiz.\n\n"
        "Menyudan foydalaning 👇",
        reply_markup=STUDENT_MAIN,
    )
