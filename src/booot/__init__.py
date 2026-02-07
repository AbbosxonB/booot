"""Core domain logic for the university service desk bot."""

from booot.models import Department, Role, Subtopic, Ticket, TicketStatus
from booot.routing import DepartmentRouter
from booot.ticketing import TicketService

__all__ = [
    "Department",
    "Role",
    "Subtopic",
    "Ticket",
    "TicketStatus",
    "DepartmentRouter",
    "TicketService",
]
