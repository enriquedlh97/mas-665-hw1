"""Task for booking meetings on Enrique's calendar."""

from datetime import datetime

from crewai import Task

from ..backends.base_backend import BookingRequest, TimeSlot
from ..backends.playwright_mcp import PlaywrightMCPBackend


def create_book_meeting_task(
    slot_data: dict,
    contact_info: dict[str, str],
    notes: str | None = None,
    guests: list[str] | None = None,
) -> Task:
    """
    Create a task to book a meeting on Enrique's calendar.

    Args:
        slot_data: Dict containing slot information (start, end, booking_url)
        contact_info: Dict with 'name' and 'email' keys
        notes: Optional meeting notes
        guests: Optional list of guest email addresses

    Returns:
        CrewAI Task for booking meetings
    """

    async def book_meeting_action() -> str:
        """Action function that actually books the meeting."""
        backend = PlaywrightMCPBackend()

        try:
            # Create TimeSlot object
            slot = TimeSlot(
                start=datetime.fromisoformat(slot_data["start"]),
                end=datetime.fromisoformat(slot_data["end"]),
                booking_url=slot_data["booking_url"],
            )

            # Create BookingRequest
            request = BookingRequest(
                slot=slot, contact=contact_info, notes=notes, guests=guests
            )

            # Book the meeting
            confirmation = await backend.book_meeting(request)

            # Format confirmation for display
            confirmation_text = f"""
Meeting Successfully Booked! 🎉

Details:
• Date: {confirmation.start.strftime("%A, %B %d, %Y")}
• Time: {confirmation.start.strftime("%I:%M %p")} - {confirmation.end.strftime("%I:%M %p")}
• Attendee: {confirmation.invitee_email}
• Status: {confirmation.status.title()}

"""

            if confirmation.meeting_link:
                confirmation_text += f"• Meeting Link: {confirmation.meeting_link}\n"

            if confirmation.calendar_invite_url:
                confirmation_text += (
                    f"• Calendar Invite: {confirmation.calendar_invite_url}\n"
                )

            if confirmation.booking_id:
                confirmation_text += f"• Booking ID: {confirmation.booking_id}\n"

            confirmation_text += "\nEnrique will receive a notification and you should receive a confirmation email shortly."

            return confirmation_text

        except Exception as e:
            return (
                f"Error booking meeting: {str(e)}. Please try again or contact support."
            )
        finally:
            await backend.close()

    return Task(
        description=f"""Book a meeting on Enrique's calendar with the provided information.

        Meeting Details:
        • Time Slot: {slot_data.get("start", "TBD")} to {slot_data.get("end", "TBD")}
        • Contact: {contact_info.get("name", "TBD")} ({contact_info.get("email", "TBD")})
        • Notes: {notes or "None"}
        • Guests: {", ".join(guests) if guests else "None"}

        Process the booking and return confirmation details.""",
        expected_output="A detailed confirmation message with meeting details, links, and next steps",
        agent=None,  # Will be assigned when task is executed
        action=book_meeting_action,
    )
