"""Base backend interface for calendar operations."""

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class TimeSlot(BaseModel):
    """Represents an available time slot."""

    start: datetime
    end: datetime
    booking_url: str
    event_type: str | None = None


class BookingRequest(BaseModel):
    """Request to book a meeting."""

    slot: TimeSlot
    contact: dict[str, str]  # {"name": "...", "email": "..."}
    notes: str | None = None
    guests: list[str] | None = None


class BookingConfirmation(BaseModel):
    """Confirmation of a successful booking."""

    status: str
    start: datetime
    end: datetime
    invitee_email: str
    meeting_link: str | None = None
    calendar_invite_url: str | None = None
    booking_id: str | None = None


class BaseBackend(ABC):
    """Abstract base class for calendar backends."""

    @abstractmethod
    async def check_availability(
        self,
        date: datetime | None = None,
        date_range: dict[str, datetime] | None = None,
    ) -> list[TimeSlot]:
        """
        Check available time slots.

        Args:
            date: Specific date to check
            date_range: Dict with 'start' and 'end' keys for range

        Returns:
            List of available time slots
        """
        pass

    @abstractmethod
    async def book_meeting(self, request: BookingRequest) -> BookingConfirmation:
        """
        Book a meeting.

        Args:
            request: Booking request with slot and contact info

        Returns:
            Booking confirmation details
        """
        pass

    @abstractmethod
    async def get_nearest_alternatives(
        self, preferred_date: datetime, limit: int = 3
    ) -> list[TimeSlot]:
        """
        Get nearest available alternatives to a preferred date.

        Args:
            preferred_date: The preferred date/time
            limit: Maximum number of alternatives to return

        Returns:
            List of alternative time slots
        """
        pass
