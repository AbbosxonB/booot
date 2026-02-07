from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class Role(str, Enum):
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ANSWERED = "ANSWERED"
    CLOSED = "CLOSED"


class Department(str, Enum):
    DEKANAT = "DEKANAT"
    OQUV_BOLIMI = "OQUV_BOLIMI"
    BUXGALTERIYA = "BUXGALTERIYA"
    MARKETING = "MARKETING"
    IT = "IT"


class Subtopic(str, Enum):
    CHAQIRUV_QOGOZI = "chaqiruv_qogozi"
    MALUMOTNOMA = "malumotnoma"
    TRANSKRIPT = "transkript"
    BAHOGA_ETIROZ = "bahoga_etiroz"
    DEKANAT_BOSHQA = "dekanat_boshqa"
    DARS_JADVALI = "dars_jadvali"
    FANLAR_ROYXATI = "fanlar_royxati"
    OQITUVCHI_ALMASHISHI = "oqituvchi_almashishi"
    AUDITORIYA_MASALALARI = "auditoriya_masalalari"
    OQUV_REJA = "oquv_reja"
    OQUV_BOLIMI_BOSHQA = "oquv_bolimi_boshqa"
    QARZDORLIK = "qarzdorlik"
    TOLV_KVITANSIYASI = "tolov_kvitansiyasi"
    STIPENDIYA = "stipendiya"
    HISOB_XATOLARI = "hisob_kitob_xatolari"
    TOLV_QAYTARISH = "tolovni_qaytarish"
    BUXGALTERIYA_BOSHQA = "buxgalteriya_boshqa"
    KONTRAKT_SUMMASI = "kontrakt_summasi"
    KONTRAKT_NUSXASI = "kontrakt_nusxasi"
    TOLV_MUDDATI = "tolov_muddati"
    MARKETING_KVITANSIYA = "marketing_kvitansiya"
    MARKETING_BOSHQA = "marketing_boshqa"
    LOGIN_PAROL = "login_parol"
    PORTAL_ISHLAMASLIGI = "portal_ishlamasligi"
    BOT_XATOSI = "telegram_bot_xatosi"
    IT_BOSHQA = "it_boshqa"


@dataclass(slots=True)
class UserProfile:
    user_id: int
    role: Role
    group: str | None = None


@dataclass(slots=True)
class Ticket:
    student_id: int
    subtopic: Subtopic
    department: Department
    summary: str
    priority: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: TicketStatus = TicketStatus.OPEN
    ticket_id: UUID = field(default_factory=uuid4)
    history: list[str] = field(default_factory=list)

    def add_history(self, message: str) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        self.history.append(f"{timestamp} - {message}")
