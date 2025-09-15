"""A consolidated module for all CrewAI tools used in the system."""

from datetime import datetime
from pathlib import Path

from crewai.tools import BaseTool


class PersonaReaderTool(BaseTool):
    """Tool for reading and providing Enrique's persona information."""

    name: str = "read_persona_information"
    description: str = """Read Enrique's complete persona information including his background,
    interests, expertise, current projects, and communication style. Use this when users
    ask about who Enrique is, what he does, his background, or his interests."""

    def _run(self) -> str:
        """Read Enrique's persona information from the data file."""
        try:
            persona_path = Path(__file__).parent.parent / "data" / "persona.md"
            if not persona_path.exists():
                return "I don't have access to Enrique's persona information at the moment."
            with open(persona_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading Enrique's persona information: {str(e)}"


class CalendarCheckerTool(BaseTool):
    """Tool for checking Enrique's calendar availability."""

    name: str = "check_calendar_availability"
    description: str = """Check Enrique's calendar for available time slots.
    Use this when a user asks about Enrique's availability or wants to see his schedule."""

    def _run(self, date_preference: str = "") -> str:
        """Check calendar availability (mocked)."""
        # In a real implementation, this would connect to a calendar API.
        # For now, we return a static, friendly response.
        return (
            "Enrique's calendar is quite flexible this week. To find the perfect time, "
            "could you please suggest a few dates and times that work for you? "
            "That will make it easier to coordinate and book a meeting."
        )


class MeetingBookerTool(BaseTool):
    """Tool for booking meetings with Enrique."""

    name: str = "book_meeting_slot"
    description: str = """Book a meeting with Enrique. Requires the meeting details including
    the proposed date and time, attendee name, and email."""

    def _run(self, meeting_details: str) -> str:
        """Book a meeting with the provided details (mocked)."""
        # In a real implementation, this would use an API to book the meeting.
        booking_id = f"ENR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return (
            f"🎉 Meeting Successfully Booked!\n"
            f"Booking ID: {booking_id}\n"
            f"Details: {meeting_details}\n\n"
            "A calendar invitation with the meeting link has been sent to the attendee. "
            "Enrique is looking forward to the conversation!"
        )
