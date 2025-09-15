"""Timezone handling utilities for the Enrique Crew system."""

import re
from datetime import datetime, time

import pytz


class TimezoneHandler:
    """Handles timezone conversion and user timezone detection."""

    # Enrique's default timezone
    ENRIQUE_TIMEZONE = pytz.timezone("America/New_York")

    # Common timezone mappings for user input
    TIMEZONE_MAPPINGS = {
        "pst": "America/Los_Angeles",
        "pdt": "America/Los_Angeles",
        "pacific": "America/Los_Angeles",
        "cst": "America/Chicago",
        "cdt": "America/Chicago",
        "central": "America/Chicago",
        "mst": "America/Denver",
        "mdt": "America/Denver",
        "mountain": "America/Denver",
        "est": "America/New_York",
        "edt": "America/New_York",
        "eastern": "America/New_York",
        "utc": "UTC",
        "gmt": "UTC",
    }

    @classmethod
    def detect_user_timezone(cls, user_input: str) -> str | None:
        """
        Detect user's timezone from their input.

        Args:
            user_input: User's message containing time information

        Returns:
            Detected timezone string or None if not found
        """
        user_input_lower = user_input.lower()

        # Look for explicit timezone mentions
        for tz_abbrev, tz_name in cls.TIMEZONE_MAPPINGS.items():
            if tz_abbrev in user_input_lower:
                return tz_name

        # Look for common timezone patterns
        timezone_patterns = [
            r"(\w+)\s+time",
            r"(\w+)\s+timezone",
            r"(\w+)\s+tz",
            r"in\s+(\w+)",
            r"(\w+)\s+zone",
        ]

        for pattern in timezone_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                tz_candidate = match.group(1).lower()
                if tz_candidate in cls.TIMEZONE_MAPPINGS:
                    return cls.TIMEZONE_MAPPINGS[tz_candidate]

        return None

    @classmethod
    def convert_to_eastern_time(
        cls,
        user_time_str: str,
        user_timezone: str,
        target_date: datetime | None = None,
    ) -> tuple[datetime, str]:
        """
        Convert user's time to Eastern Time.

        Args:
            user_time_str: Time string from user (e.g., "2pm", "14:00")
            user_timezone: User's timezone
            target_date: Date to use for conversion (defaults to today)

        Returns:
            Tuple of (converted_datetime, conversion_message)
        """
        if target_date is None:
            target_date = datetime.now()

        # Parse user time
        user_time = cls._parse_time_string(user_time_str)
        if user_time is None:
            raise ValueError(f"Could not parse time: {user_time_str}")

        # Create datetime in user's timezone
        user_tz = pytz.timezone(user_timezone)
        user_datetime = user_tz.localize(
            datetime.combine(target_date.date(), user_time)
        )

        # Convert to Eastern Time
        eastern_datetime = user_datetime.astimezone(cls.ENRIQUE_TIMEZONE)

        # Create conversion message
        user_tz_name = cls._get_friendly_timezone_name(user_timezone)
        conversion_message = (
            f"I'll convert {user_time_str} {user_tz_name} to "
            f"{eastern_datetime.strftime('%I:%M %p')} Eastern Time for Enrique's calendar."
        )

        return eastern_datetime, conversion_message

    @classmethod
    def _parse_time_string(cls, time_str: str) -> time | None:
        """Parse various time string formats."""
        time_str = time_str.strip().lower()

        # Handle formats like "2pm", "2:30pm", "14:00", "2:00 PM"
        patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm)?",
            r"(\d{1,2})\s*(am|pm)",
            r"(\d{1,2}):(\d{2})",
        ]

        for pattern in patterns:
            match = re.match(pattern, time_str)
            if match:
                groups = match.groups()

                if len(groups) == 3 and groups[2]:  # Has AM/PM
                    hour = int(groups[0])
                    minute = int(groups[1]) if groups[1] else 0
                    period = groups[2]

                    if period == "pm" and hour != 12:
                        hour += 12
                    elif period == "am" and hour == 12:
                        hour = 0

                    return time(hour, minute)

                elif len(groups) == 2:  # 24-hour format
                    hour = int(groups[0])
                    minute = int(groups[1])

                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return time(hour, minute)

        return None

    @classmethod
    def _get_friendly_timezone_name(cls, timezone_str: str) -> str:
        """Get a friendly timezone name for display."""
        friendly_names = {
            "America/Los_Angeles": "Pacific Time",
            "America/Chicago": "Central Time",
            "America/Denver": "Mountain Time",
            "America/New_York": "Eastern Time",
            "UTC": "UTC",
        }
        return friendly_names.get(timezone_str, timezone_str)

    @classmethod
    def format_time_with_timezone(cls, dt: datetime, timezone_str: str) -> str:
        """Format datetime with timezone for display."""
        tz = pytz.timezone(timezone_str)
        local_dt = dt.astimezone(tz)
        friendly_tz = cls._get_friendly_timezone_name(timezone_str)

        return f"{local_dt.strftime('%I:%M %p')} {friendly_tz}"
