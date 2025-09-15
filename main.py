"""Main terminal interface for Enrique's Persona AI Agent."""

from crewai import Crew, Process

from crew.agents.persona_agent import create_persona_agent
from crew.config.settings import settings


class EnriqueCrewSystem:
    """
    Manages Enrique's personal AI agent.

    This system uses a single PersonaAgent with multiple tools to handle all user
    interactions. Enrique responds as himself and has access to tools for:
    - Sharing his background and interests (PersonaReaderTool)
    - Checking calendar availability (CalendarCheckerTool)
    - Booking meetings (MeetingBookerTool)
    """

    def __init__(self) -> None:
        """
        Initializes the system by creating Enrique's persona agent.

        Enrique has access to multiple tools to handle all user interactions
        including questions about himself and scheduling requests.
        """
        # Create Enrique's persona agent with all necessary tools
        self.persona_agent = create_persona_agent()

        # Create the Crew with Enrique's agent
        self.crew = self._create_crew()

    def _create_crew(self) -> Crew:
        """
        Creates the CrewAI crew with Enrique's persona agent.

        Enrique handles all user interactions using his available tools.
        """
        return Crew(
            agents=[self.persona_agent],  # Enrique handles everything
            tasks=[],  # Tasks created dynamically
            process=Process.sequential,
            verbose=settings.verbose,
            memory=settings.memory_enabled,
        )

    def process_user_input(self, user_input: str) -> str:
        """
        Processes a user's message by creating a task for Enrique.

        Enrique responds as himself using his available tools to handle
        questions about himself or scheduling requests.

        Args:
            user_input: The user's message

        Returns:
            str: Enrique's response
        """
        from crewai import Task

        # Create a simple task for Enrique to handle
        enrique_task = Task(
            description=f"""Continue the conversation as Enrique Diaz de Leon Hicks.

            The user just said: "{user_input}"

            You are Enrique, an AI Studio student. Respond naturally and personally:
            - Remember what we've discussed in this conversation
            - Use your PersonaReaderTool to share details about your background when relevant
            - If they ask about scheduling, use your calendar tools to help
            - Always speak in first person as yourself (Enrique)
            - Be conversational and remember the user's name if they've shared it

            Continue this conversation naturally.""",
            expected_output="A natural, contextual response from Enrique that shows conversation continuity",
            agent=self.persona_agent,
        )

        # Add the task to the crew (preserves memory across interactions)
        self.crew.tasks.append(enrique_task)
        result = self.crew.kickoff()
        return str(result)


def main() -> None:
    """Main application entry point."""
    print("🤖 Acting as Enrique (AI Studio Persona)")
    print("========================================")
    print("You are now chatting with me, Enrique. Ask me anything!")
    print("Press Ctrl+C to exit the chat.")
    print("========================================")

    if not settings.openai_api_key:
        print(
            "⚠️  Warning: OPENAI_API_KEY not set. The agent may not function correctly."
        )

    crew_system = EnriqueCrewSystem()
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            response = crew_system.process_user_input(user_input)
            print(f"\nEnrique: {response}\n")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}\n")


if __name__ == "__main__":
    main()
