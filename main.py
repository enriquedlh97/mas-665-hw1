"""Main terminal interface for the Enrique Crew AI system."""

import asyncio
import sys
from datetime import datetime
from typing import Any

from crew import (
    create_availability_agent,
    create_chat_agent,
    create_persona_agent,
    create_scheduler_agent,
)
from crew.config.settings import settings
from crew.tasks import (
    create_answer_persona_task,
    create_book_meeting_task,
    create_check_availability_task,
    create_orchestrate_conversation_task,
)


class EnriqueCrewInterface:
    """Main interface for interacting with Enrique's Crew AI system."""

    def __init__(self) -> None:
        """Initialize the Crew AI system."""
        self.agents = self._create_agents()
        self.conversation_state: dict[str, Any] = {
            "current_step": "greeting",
            "pending_booking": None,
            "selected_slot": None,
            "contact_info": {},
        }

    def _create_agents(self) -> dict[str, Any]:
        """Create all CrewAI agents."""
        return {
            "chat": create_chat_agent(),
            "availability": create_availability_agent(),
            "scheduler": create_scheduler_agent(),
            "persona": create_persona_agent(),
        }

    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and return appropriate response.

        Args:
            user_input: User's message

        Returns:
            Response from the appropriate agent
        """
        try:
            # Handle special commands
            if user_input.startswith(":"):
                return self._handle_special_command(user_input)

            # Create orchestration task
            orchestration_task = create_orchestrate_conversation_task(user_input)
            orchestration_task.agent = self.agents["chat"]

            # Execute orchestration
            result = await orchestration_task.execute()

            # Determine next steps based on result
            if "availability" in result.lower():
                return await self._handle_availability_request(user_input)
            elif "persona" in result.lower():
                return await self._handle_persona_request(user_input)
            elif "booking" in result.lower():
                return await self._handle_booking_request(user_input)
            else:
                return str(result)

        except Exception as e:
            return f"Error processing your request: {str(e)}"

    async def _handle_availability_request(self, user_input: str) -> str:
        """Handle availability checking requests."""
        # Extract date information from user input
        date_info = self._extract_date_from_input(user_input)

        # Create availability task
        if date_info:
            availability_task = create_check_availability_task(target_date=date_info)
        else:
            # Default to next 7 days
            availability_task = create_check_availability_task()

        availability_task.agent = self.agents["availability"]

        # Execute task
        result = await availability_task.execute()

        # Update conversation state
        self.conversation_state["current_step"] = "availability_shown"

        return str(result)

    async def _handle_persona_request(self, user_input: str) -> str:
        """Handle persona questions."""
        # Create persona task
        persona_task = create_answer_persona_task(user_input)
        persona_task.agent = self.agents["persona"]

        # Execute task
        result = await persona_task.execute()

        return str(result)

    async def _handle_booking_request(self, user_input: str) -> str:
        """Handle booking requests."""
        if self.conversation_state["current_step"] == "greeting":
            # First, check availability
            return await self._handle_availability_request(user_input)
        elif self.conversation_state["current_step"] == "availability_shown":
            # User is selecting a slot
            return await self._handle_slot_selection(user_input)
        elif self.conversation_state["current_step"] == "collecting_info":
            # User is providing contact information
            return await self._handle_contact_collection(user_input)
        else:
            return "I'm not sure what you'd like to do. Please try again."

    async def _handle_slot_selection(self, user_input: str) -> str:
        """Handle slot selection."""
        # Extract slot number from input
        try:
            slot_number = int(user_input.strip())
            if 1 <= slot_number <= 5:  # Assuming we show top 5 slots
                self.conversation_state["selected_slot"] = slot_number
                self.conversation_state["current_step"] = "collecting_info"
                return """Great! I've noted your slot selection.

Now I need some information to complete the booking:
• Your full name
• Your email address
• Any notes about the meeting (optional)
• Guest email addresses (optional)

Please provide your name and email first."""
            else:
                return "Please select a valid slot number (1-5)."
        except ValueError:
            return "Please enter a number to select a slot."

    async def _handle_contact_collection(self, user_input: str) -> str:
        """Handle contact information collection."""
        # Simple parsing of contact info
        if "@" in user_input:
            # Extract email
            email = (
                user_input.split()[-1]
                if user_input.split()[-1].count("@") == 1
                else None
            )
            if email:
                contact_info = self.conversation_state["contact_info"]
                if isinstance(contact_info, dict):
                    contact_info["email"] = email
                    # Extract name (everything before email)
                    name = (
                        " ".join(user_input.split()[:-1])
                        if len(user_input.split()) > 1
                        else "Unknown"
                    )
                    contact_info["name"] = name

                # Create booking task
                return await self._create_booking()
            else:
                return "Please provide a valid email address."
        else:
            return "Please provide your name and email address."

    async def _create_booking(self) -> str:
        """Create the actual booking."""
        try:
            # Mock slot data (in real implementation, this would come from availability check)
            slot_data = {
                "start": datetime.now().isoformat(),
                "end": (
                    datetime.now().replace(hour=datetime.now().hour + 1)
                ).isoformat(),
                "booking_url": "https://calendly.com/mock-booking",
            }

            # Create booking task
            contact_info = self.conversation_state["contact_info"]
            if isinstance(contact_info, dict):
                booking_task = create_book_meeting_task(
                    slot_data=slot_data,
                    contact_info=contact_info,
                )
            else:
                return "Error: Contact information not found. Please try again."
            booking_task.agent = self.agents["scheduler"]

            # Execute booking
            result = await booking_task.execute()

            # Reset conversation state
            self.conversation_state = {
                "current_step": "greeting",
                "pending_booking": None,
                "selected_slot": None,
                "contact_info": {},
            }

            return str(result)

        except Exception as e:
            return f"Error creating booking: {str(e)}"

    def _extract_date_from_input(self, user_input: str) -> datetime | None:
        """Extract date information from user input."""
        # Simple date extraction (in real implementation, use more sophisticated parsing)
        import re

        # Look for common date patterns
        patterns = [
            r"today",
            r"tomorrow",
            r"this week",
            r"next week",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]

        for pattern in patterns:
            if re.search(pattern, user_input.lower()):
                if "today" in user_input.lower():
                    return datetime.now()
                elif "tomorrow" in user_input.lower():
                    return datetime.now().replace(day=datetime.now().day + 1)
                elif "this week" in user_input.lower():
                    return datetime.now().replace(day=datetime.now().day + 1)
                elif "next week" in user_input.lower():
                    return datetime.now().replace(day=datetime.now().day + 7)

        return None

    def _handle_special_command(self, command: str) -> str:
        """Handle special terminal commands."""
        if command == ":help":
            return """
Available commands:
:help     - Show this help message
:reset    - Clear conversation state
:debug    - Show current conversation state
:quit     - Exit the application
"""
        elif command == ":reset":
            self.conversation_state = {
                "current_step": "greeting",
                "pending_booking": None,
                "selected_slot": None,
                "contact_info": {},
            }
            return "Conversation state reset. How can I help you?"
        elif command == ":debug":
            return f"Current state: {self.conversation_state}"
        elif command == ":quit":
            sys.exit(0)
        else:
            return f"Unknown command: {command}. Type :help for available commands."


async def main() -> None:
    """Main application entry point."""
    print("🤖 Enrique Crew AI System")
    print("=" * 50)
    print("Welcome! I'm Enrique's personal assistant.")
    print("I can help you schedule meetings or learn about Enrique.")
    print("Type :help for commands or just start chatting!")
    print("=" * 50)

    # Initialize the interface
    interface = EnriqueCrewInterface()

    # Check configuration
    if not settings.openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set. Some features may not work.")

    if not settings.calendly_link or "your-handle" in settings.calendly_link:
        print("⚠️  Warning: CALENDLY_LINK not properly configured.")

    print(f"📅 Calendly Link: {settings.calendly_link}")
    print(f"🔗 MCP Server: {settings.mcp_server_url}")
    print()

    # Main conversation loop
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Process input
            response = await interface.process_user_input(user_input)

            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    asyncio.run(main())
