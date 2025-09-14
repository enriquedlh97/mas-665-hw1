"""Playwright MCP backend for Calendly interaction."""

from datetime import datetime, timedelta

import httpx

from ..config.settings import settings
from .base_backend import BaseBackend, BookingConfirmation, BookingRequest, TimeSlot


class PlaywrightMCPBackend(BaseBackend):
    """Backend implementation using Playwright MCP server."""

    def __init__(self) -> None:
        self.mcp_url = settings.mcp_server_url
        self.calendly_link = settings.calendly_link
        self.client = httpx.AsyncClient(timeout=30.0)

    async def check_availability(
        self,
        date: datetime | None = None,
        date_range: dict[str, datetime] | None = None,
    ) -> list[TimeSlot]:
        """
        Check available time slots using Playwright MCP.

        This method sends a request to the MCP server to:
        1. Navigate to the Calendly page
        2. Extract available slots for the given date/range
        3. Return structured slot data
        """
        try:
            # Prepare the MCP request payload
            mcp_request = {
                "method": "check_calendly_availability",
                "params": {
                    "calendly_url": self.calendly_link,
                    "target_date": date.isoformat() if date else None,
                    "date_range": {
                        "start": date_range["start"].isoformat(),
                        "end": date_range["end"].isoformat(),
                    }
                    if date_range
                    else None,
                },
            }

            # Send request to MCP server
            response = await self.client.post(f"{self.mcp_url}/mcp", json=mcp_request)
            response.raise_for_status()

            # Parse response and convert to TimeSlot objects
            mcp_response = response.json()
            slots_data = mcp_response.get("result", {}).get("slots", [])

            time_slots = []
            for slot_data in slots_data:
                time_slots.append(
                    TimeSlot(
                        start=datetime.fromisoformat(slot_data["start"]),
                        end=datetime.fromisoformat(slot_data["end"]),
                        booking_url=slot_data["booking_url"],
                        event_type=slot_data.get("event_type"),
                    )
                )

            return time_slots

        except Exception as e:
            print(f"Error checking availability via MCP: {e}")
            return []

    async def book_meeting(self, request: BookingRequest) -> BookingConfirmation:
        """
        Book a meeting using Playwright MCP.

        This method sends a request to the MCP server to:
        1. Navigate to the booking URL
        2. Fill out the booking form
        3. Submit and extract confirmation details
        """
        try:
            # Prepare the MCP request payload
            mcp_request = {
                "method": "book_calendly_meeting",
                "params": {
                    "booking_url": request.slot.booking_url,
                    "contact_info": request.contact,
                    "notes": request.notes,
                    "guests": request.guests or [],
                },
            }

            # Send request to MCP server
            response = await self.client.post(f"{self.mcp_url}/mcp", json=mcp_request)
            response.raise_for_status()

            # Parse response and create confirmation
            mcp_response = response.json()
            booking_data = mcp_response.get("result", {})

            return BookingConfirmation(
                status="booked",
                start=request.slot.start,
                end=request.slot.end,
                invitee_email=request.contact["email"],
                meeting_link=booking_data.get("meeting_link"),
                calendar_invite_url=booking_data.get("calendar_invite_url"),
                booking_id=booking_data.get("booking_id"),
            )

        except Exception as e:
            print(f"Error booking meeting via MCP: {e}")
            # Return a basic confirmation even if MCP fails
            return BookingConfirmation(
                status="pending",
                start=request.slot.start,
                end=request.slot.end,
                invitee_email=request.contact["email"],
            )

    async def get_nearest_alternatives(
        self, preferred_date: datetime, limit: int = 3
    ) -> list[TimeSlot]:
        """
        Get nearest available alternatives by checking a range around the preferred date.
        """
        # Check availability for the next 7 days starting from preferred date
        start_date = preferred_date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)

        date_range = {"start": start_date, "end": end_date}
        all_slots = await self.check_availability(date_range=date_range)

        # Sort by proximity to preferred date
        all_slots.sort(
            key=lambda slot: abs((slot.start - preferred_date).total_seconds())
        )

        return all_slots[:limit]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
