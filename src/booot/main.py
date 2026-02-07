import asyncio
import structlog

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from booot.config import settings
from booot.logging_setup import setup_logging
from booot.db import engine, Base, SessionLocal
from booot.seed import seed_if_needed
from booot.handlers.common import router as common_router
from booot.handlers.student import router as student_router
from booot.handlers.staff import router as staff_router
from booot.handlers.superadmin import router as superadmin_router
from booot.services.reminders import tickets_needing_reminder, tickets_needing_escalation

log = structlog.get_logger()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await seed_if_needed(session)


async def reminder_job(bot: Bot) -> None:
    async with SessionLocal() as session:  # type: AsyncSession
        remind = await tickets_needing_reminder(session)
        esc = await tickets_needing_escalation(session)

    # Hozircha: log + superadminlarga ping (keyin admin panelga “escalated queue”)
    for t in esc:
        for sid in settings.superadmin_ids():
            try:
                await bot.send_message(sid, f"🚨 ESCALATION: {t.public_id} javobsiz qolmoqda.")
            except Exception:
                pass

    for t in remind:
        # assigned staff bo‘lsa unga, bo‘lmasa superadmin
        targets = []
        if t.assigned_staff_id:
            # staff tg_id olish uchun query kerak (keyin qo‘shamiz)
            pass
        targets = targets or list(settings.superadmin_ids())
        for sid in targets:
            try:
                await bot.send_message(sid, f"⏰ Reminder: {t.public_id} hali yakunlanmagan ({t.status}).")
            except Exception:
                pass


async def main() -> None:
    setup_logging()
    await init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common_router)
    dp.include_router(student_router)
    dp.include_router(staff_router)
    dp.include_router(superadmin_router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(reminder_job, "interval", minutes=5, args=[bot])
    scheduler.start()

    log.info("bot_started")
    await dp.start_polling(bot)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
