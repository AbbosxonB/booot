from __future__ import annotations

from dataclasses import dataclass

from booot.models import Department, Subtopic


@dataclass(frozen=True, slots=True)
class SubtopicRule:
    department: Department
    priority: int
    requires_comment: bool = False


SUBTOPIC_RULES: dict[Subtopic, SubtopicRule] = {
    Subtopic.CHAQIRUV_QOGOZI: SubtopicRule(Department.DEKANAT, priority=3),
    Subtopic.MALUMOTNOMA: SubtopicRule(Department.DEKANAT, priority=3),
    Subtopic.TRANSKRIPT: SubtopicRule(Department.DEKANAT, priority=3),
    Subtopic.BAHOGA_ETIROZ: SubtopicRule(Department.DEKANAT, priority=5),
    Subtopic.DEKANAT_BOSHQA: SubtopicRule(
        Department.DEKANAT, priority=3, requires_comment=True
    ),
    Subtopic.DARS_JADVALI: SubtopicRule(Department.OQUV_BOLIMI, priority=3),
    Subtopic.FANLAR_ROYXATI: SubtopicRule(Department.OQUV_BOLIMI, priority=3),
    Subtopic.OQITUVCHI_ALMASHISHI: SubtopicRule(Department.OQUV_BOLIMI, priority=4),
    Subtopic.AUDITORIYA_MASALALARI: SubtopicRule(Department.OQUV_BOLIMI, priority=3),
    Subtopic.OQUV_REJA: SubtopicRule(Department.OQUV_BOLIMI, priority=3),
    Subtopic.OQUV_BOLIMI_BOSHQA: SubtopicRule(
        Department.OQUV_BOLIMI, priority=3, requires_comment=True
    ),
    Subtopic.QARZDORLIK: SubtopicRule(Department.BUXGALTERIYA, priority=4),
    Subtopic.TOLV_KVITANSIYASI: SubtopicRule(Department.BUXGALTERIYA, priority=3),
    Subtopic.STIPENDIYA: SubtopicRule(Department.BUXGALTERIYA, priority=3),
    Subtopic.HISOB_XATOLARI: SubtopicRule(Department.BUXGALTERIYA, priority=4),
    Subtopic.TOLV_QAYTARISH: SubtopicRule(Department.BUXGALTERIYA, priority=4),
    Subtopic.BUXGALTERIYA_BOSHQA: SubtopicRule(
        Department.BUXGALTERIYA, priority=3, requires_comment=True
    ),
    Subtopic.KONTRAKT_SUMMASI: SubtopicRule(Department.MARKETING, priority=3),
    Subtopic.KONTRAKT_NUSXASI: SubtopicRule(Department.MARKETING, priority=3),
    Subtopic.TOLV_MUDDATI: SubtopicRule(Department.MARKETING, priority=3),
    Subtopic.MARKETING_KVITANSIYA: SubtopicRule(Department.MARKETING, priority=3),
    Subtopic.MARKETING_BOSHQA: SubtopicRule(
        Department.MARKETING, priority=3, requires_comment=True
    ),
    Subtopic.LOGIN_PAROL: SubtopicRule(Department.IT, priority=4),
    Subtopic.PORTAL_ISHLAMASLIGI: SubtopicRule(Department.IT, priority=4),
    Subtopic.BOT_XATOSI: SubtopicRule(Department.IT, priority=4),
    Subtopic.IT_BOSHQA: SubtopicRule(Department.IT, priority=3, requires_comment=True),
}


class DepartmentRouter:
    def resolve(self, subtopic: Subtopic) -> SubtopicRule:
        if subtopic not in SUBTOPIC_RULES:
            raise ValueError(f"Unknown subtopic: {subtopic}")
        return SUBTOPIC_RULES[subtopic]
