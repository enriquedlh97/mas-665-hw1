"""Task for orchestrating the overall conversation flow."""

import re

from crewai import Task

from ..utils.timezone_handler import TimezoneHandler


def create_orchestrate_conversation_task(user_message: str) -> Task:
    """
    Create a task to orchestrate the conversation flow.

    Args:
        user_message: The user's input message

    Returns:
        CrewAI Task for conversation orchestration
    """

    def orchestrate_conversation_action() -> str:
        """Action function that determines the conversation flow."""
        message_lower = user_message.lower()

        # Detect intent
        intent = detect_user_intent(message_lower)

        # Check for time conversion first
        time_conversion_msg = handle_time_conversion(user_message)

        if intent == "booking":
            response = handle_booking_intent(user_message)
            if time_conversion_msg:
                response = time_conversion_msg + "\n\n" + response
            return response
        elif intent == "persona":
            return handle_persona_intent(user_message)
        elif intent == "availability":
            response = handle_availability_intent(user_message)
            if time_conversion_msg:
                response = time_conversion_msg + "\n\n" + response
            return response
        else:
            return handle_general_intent(user_message)

    def detect_user_intent(message: str) -> str:
        """Detect the user's intent from their message."""
        booking_keywords = [
            "meet",
            "schedule",
            "book",
            "appointment",
            "call",
            "chat",
            "talk",
        ]
        persona_keywords = [
            "who",
            "what",
            "about",
            "background",
            "bio",
            "tell me about",
        ]
        availability_keywords = ["available", "free", "when can", "what time"]

        if any(keyword in message for keyword in booking_keywords):
            return "booking"
        elif any(keyword in message for keyword in persona_keywords):
            return "persona"
        elif any(keyword in message for keyword in availability_keywords):
            return "availability"
        else:
            return "general"

    def handle_booking_intent(message: str) -> str:
        """Handle booking-related messages."""
        # Extract date information
        date_info = extract_date_info(message)

        # Check for timezone information
        user_timezone = TimezoneHandler.detect_user_timezone(message)

        if date_info:
            response = f"""I understand you'd like to schedule a meeting with Enrique.

I found a date preference: {date_info}"""

            # Add timezone conversion message if needed
            if user_timezone and user_timezone != "America/New_York":
                response += """

I'll convert any times you mention to Eastern Time for Enrique's calendar."""

            response += """

Let me check Enrique's availability for that time. I'll delegate this to our availability specialist."""

            return response
        else:
            return """I understand you'd like to schedule a meeting with Enrique.

Do you have a specific date or time in mind, or would you like me to check his availability for this week?"""

    def handle_persona_intent(message: str) -> str:
        """Handle persona-related messages."""
        return """I'd be happy to tell you about Enrique!

Let me delegate this to our persona specialist who knows all about Enrique's background and interests."""

    def handle_availability_intent(message: str) -> str:
        """Handle availability-related messages."""
        return """I can help you check Enrique's availability!

Let me connect you with our availability specialist to find the best times for your meeting."""

    def handle_general_intent(message: str) -> str:
        """Handle general messages."""
        return """Hello! I'm Enrique's personal assistant. I can help you with:

• Scheduling a meeting with Enrique
• Learning about Enrique's background and interests
• Checking Enrique's availability

What would you like to do today?"""

    def extract_date_info(message: str) -> str | None:
        """Extract date information from the message."""
        # Simple date extraction patterns
        patterns = [
            r"(today|tomorrow)",
            r"(this|next)\s+(week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def handle_time_conversion(message: str) -> str | None:
        """Handle time conversion when user specifies a time in different timezone."""
        # Look for time patterns with timezone
        time_patterns = [
            r"(\d{1,2}:\d{2}\s*(am|pm)?)\s*(pst|pdt|pacific|cst|cdt|central|mst|mdt|mountain|est|edt|eastern|utc|gmt)",
            r"(\d{1,2}\s*(am|pm))\s*(pst|pdt|pacific|cst|cdt|central|mst|mdt|mountain|est|edt|eastern|utc|gmt)",
        ]

        for pattern in time_patterns:
            match = re.search(pattern, message.lower())
            if match:
                time_str = match.group(1)
                timezone_abbrev = match.group(-1)  # Last group is timezone

                # Convert timezone abbreviation to full name
                timezone_mapping = {
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

                user_timezone = timezone_mapping.get(timezone_abbrev)
                if user_timezone and user_timezone != "America/New_York":
                    try:
                        converted_time, conversion_msg = (
                            TimezoneHandler.convert_to_eastern_time(
                                time_str, user_timezone
                            )
                        )
                        return conversion_msg
                    except ValueError:
                        return f"I'll convert {time_str} {timezone_abbrev.upper()} to Eastern Time for Enrique's calendar."

        return None

    return Task(
        description=f"""Analyze the user's message and determine the appropriate response and next steps.

        User message: "{user_message}"

        Determine if this is a:
        1. Booking request (scheduling a meeting)
        2. Persona question (learning about Enrique)
        3. Availability inquiry (checking when Enrique is free)
        4. General greeting or unclear intent

        Provide an appropriate response and suggest next steps.""",
        expected_output="A clear response that acknowledges the user's intent and suggests appropriate next steps",
        agent=None,  # Will be assigned when task is executed
        action=orchestrate_conversation_action,
    )
