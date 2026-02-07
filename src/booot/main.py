from __future__ import annotations

from datetime import timedelta

from booot.models import Subtopic
from booot.routing import DepartmentRouter
from booot.ticketing import TicketRateLimiter, TicketService


def main() -> None:
    router = DepartmentRouter()
    rate_limiter = TicketRateLimiter(window=timedelta(minutes=30))
    service = TicketService(router=router, rate_limiter=rate_limiter)

    ticket = service.create_ticket(
        student_id=1001,
        subtopic=Subtopic.BAHOGA_ETIROZ,
        summary="Bahoga e'tirozim bor",
        extra_comment="Final imtihon bahosi noto'g'ri hisoblangan.",
    )
    print(
        "Created ticket",
        ticket.ticket_id,
        "department=",
        ticket.department.value,
        "priority=",
        ticket.priority,
    )


if __name__ == "__main__":
    main()
