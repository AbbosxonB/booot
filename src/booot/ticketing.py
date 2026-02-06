from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from booot.models import Department, Subtopic, Ticket
from booot.routing import DepartmentRouter


@dataclass(slots=True)
class TicketRateLimiter:
    window: timedelta
    last_ticket_at: dict[int, datetime] = field(default_factory=dict)

    def can_create(self, student_id: int, now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        last = self.last_ticket_at.get(student_id)
        return last is None or (now - last) >= self.window

    def register(self, student_id: int, now: datetime | None = None) -> None:
        self.last_ticket_at[student_id] = now or datetime.utcnow()


@dataclass(slots=True)
class TicketService:
    router: DepartmentRouter
    rate_limiter: TicketRateLimiter
    tickets: dict[str, Ticket] = field(default_factory=dict)

    def create_ticket(
        self,
        *,
        student_id: int,
        subtopic: Subtopic,
        summary: str,
        extra_comment: str | None = None,
        now: datetime | None = None,
    ) -> Ticket:
        if not self.rate_limiter.can_create(student_id, now=now):
            raise ValueError("Ticket limit reached for this student")

        rule = self.router.resolve(subtopic)
        self._validate_comment(rule.department, subtopic, extra_comment)

        ticket = Ticket(
            student_id=student_id,
            subtopic=subtopic,
            department=rule.department,
            summary=summary,
            priority=rule.priority,
            created_at=now or datetime.utcnow(),
        )
        ticket.add_history("Ticket created")
        if extra_comment:
            ticket.add_history(f"Student comment: {extra_comment}")

        self.tickets[str(ticket.ticket_id)] = ticket
        self.rate_limiter.register(student_id, now=now)
        return ticket

    def list_department_tickets(self, department: Department) -> list[Ticket]:
        return [ticket for ticket in self.tickets.values() if ticket.department == department]

    def _validate_comment(
        self, department: Department, subtopic: Subtopic, extra_comment: str | None
    ) -> None:
        rule = self.router.resolve(subtopic)
        if rule.requires_comment and not extra_comment:
            raise ValueError(
                f"Extra comment is required for {department.value} / {subtopic.value}"
            )
