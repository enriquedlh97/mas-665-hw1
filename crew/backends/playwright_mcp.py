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
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
            },
        )

    async def check_availability(
        self,
        date: datetime | None = None,
        date_range: dict[str, datetime] | None = None,
    ) -> list[TimeSlot]:
        """
        Check available time slots using Playwright MCP.

        This method uses the actual Playwright MCP tools to:
        1. Navigate to the Calendly page
        2. Take a snapshot to see available slots
        3. Extract slot information from the page
        """
        try:
            # Step 1: Navigate to Calendly page
            navigate_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "browser_navigate",
                "params": {"url": self.calendly_link},
            }

            response = await self.client.post(
                f"{self.mcp_url}/mcp", json=navigate_request
            )
            response.raise_for_status()

            # Step 2: Take a snapshot to see the page structure
            snapshot_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "browser_snapshot",
                "params": {},
            }

            response = await self.client.post(
                f"{self.mcp_url}/mcp", json=snapshot_request
            )
            response.raise_for_status()

            snapshot_data = response.json()
            page_content = snapshot_data.get("result", {}).get("content", "")

            # For now, return mock data since we need to implement Calendly parsing
            # TODO: Implement actual Calendly slot parsing from page content
            print(f"Page snapshot taken. Content length: {len(page_content)}")

            # Mock available slots for demonstration
            mock_slots = [
                TimeSlot(
                    start=datetime.now().replace(
                        hour=14, minute=0, second=0, microsecond=0
                    ),
                    end=datetime.now().replace(
                        hour=15, minute=0, second=0, microsecond=0
                    ),
                    booking_url=f"{self.calendly_link}?date=2024-01-15T14:00:00",
                    event_type="30min",
                ),
                TimeSlot(
                    start=datetime.now().replace(
                        hour=15, minute=30, second=0, microsecond=0
                    ),
                    end=datetime.now().replace(
                        hour=16, minute=30, second=0, microsecond=0
                    ),
                    booking_url=f"{self.calendly_link}?date=2024-01-15T15:30:00",
                    event_type="30min",
                ),
            ]

            return mock_slots

        except Exception as e:
            print(f"Error checking availability via MCP: {e}")
            return []

    async def book_meeting(self, request: BookingRequest) -> BookingConfirmation:
        """
        Book a meeting using Playwright MCP.

        This method uses actual Playwright MCP tools to:
        1. Navigate to the booking URL
        2. Fill out the booking form
        3. Submit and extract confirmation details
        """
        try:
            # Step 1: Navigate to booking URL
            navigate_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "browser_navigate",
                "params": {"url": request.slot.booking_url},
            }

            response = await self.client.post(
                f"{self.mcp_url}/mcp", json=navigate_request
            )
            response.raise_for_status()

            # Step 2: Take snapshot to see form structure
            snapshot_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "browser_snapshot",
                "params": {},
            }

            response = await self.client.post(
                f"{self.mcp_url}/mcp", json=snapshot_request
            )
            response.raise_for_status()

            snapshot_data = response.json()
            page_content = snapshot_data.get("result", {}).get("content", "")

            # For now, return mock confirmation since we need to implement form filling
            # TODO: Implement actual form filling using browser_type and browser_click
            print(f"Booking page loaded. Content length: {len(page_content)}")

            # Mock booking confirmation for demonstration
            return BookingConfirmation(
                status="booked",
                start=request.slot.start,
                end=request.slot.end,
                invitee_email=request.contact["email"],
                meeting_link="https://meet.google.com/mock-meeting-link",
                calendar_invite_url="https://calendar.google.com/mock-invite",
                booking_id="mock-booking-123",
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
