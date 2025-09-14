"""Task for checking Enrique's calendar availability."""

from datetime import datetime

from crewai import Task

from ..backends.playwright_mcp import PlaywrightMCPBackend


def create_check_availability_task(
    target_date: datetime | None = None, date_range: dict[str, datetime] | None = None
) -> Task:
    """
    Create a task to check Enrique's calendar availability.

    Args:
        target_date: Specific date to check
        date_range: Dict with 'start' and 'end' keys for range checking

    Returns:
        CrewAI Task for availability checking
    """

    async def check_availability_action() -> str:
        """Action function that actually checks availability."""
        backend = PlaywrightMCPBackend()

        try:
            if target_date:
                slots = await backend.check_availability(date=target_date)
            elif date_range:
                slots = await backend.check_availability(date_range=date_range)
            else:
                # Default to checking next 7 days
                from datetime import timedelta

                start_date = datetime.now().replace(
                    hour=9, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=7)
                slots = await backend.check_availability(
                    date_range={"start": start_date, "end": end_date}
                )

            # Format slots for display
            if not slots:
                return "No available slots found for the requested time period. Would you like me to suggest alternative times?"

            slot_info = []
            for i, slot in enumerate(slots[:5], 1):  # Show top 5 slots
                slot_info.append(
                    f"{i}. {slot.start.strftime('%A, %B %d at %I:%M %p')} - "
                    f"{slot.end.strftime('%I:%M %p')}"
                )

            result = "Available time slots:\n" + "\n".join(slot_info)
            if len(slots) > 5:
                result += f"\n\n... and {len(slots) - 5} more slots available."

            return result

        except Exception as e:
            return f"Error checking availability: {str(e)}"
        finally:
            await backend.close()

    return Task(
        description=f"""Check Enrique's calendar availability for the requested time period.

        {"Target date: " + target_date.strftime("%Y-%m-%d") if target_date else ""}
        {"Date range: " + f"{date_range['start'].strftime('%Y-%m-%d')} to {date_range['end'].strftime('%Y-%m-%d')}" if date_range else ""}

        Return a formatted list of available time slots with dates and times.
        If no slots are available, suggest checking alternative time periods.""",
        expected_output="A formatted list of available time slots with dates, times, and booking information",
        agent=None,  # Will be assigned when task is executed
        action=check_availability_action,
    )
