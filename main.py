"""Main terminal interface for Enrique's Persona AI Agent."""

import sys

from crewai import Crew, Process, Task

from crew.agents.persona_agent import create_persona_agent
from crew.config.settings import settings


class EnriqueCrewSystem:
    """
    Manages the CrewAI agents and tasks for Enrique's personal AI.
    This system is designed to be modular and easily extendible.
    """

    def __init__(self) -> None:
        """
        Initializes the system by creating the necessary agents.
        Currently, only the Persona Agent is active to act as Enrique.
        """
        # Create the primary agent
        self.persona_agent = create_persona_agent()

        # Future agents can be initialized here when ready
        # e.g., self.scheduler_agent = create_scheduler_agent()

        # Create the Crew with the active agents
        self.crew = self._create_crew()

    def _create_crew(self) -> Crew:
        """
        Creates the CrewAI crew with all the active agents.
        """
        return Crew(
            agents=[self.persona_agent],  # Add other agents to this list later
            tasks=[],
            process=Process.sequential,
            verbose=True,
            memory=True,
        )

    def process_user_input(self, user_input: str) -> str:
        """
        Processes a user's message by creating and running a task for the persona agent.
        """
        if user_input.lower() in [":quit", "quit", "exit"]:
            print("\n👋 Goodbye! Thanks for chatting.")
            sys.exit(0)

        # The task is explicitly defined for the persona agent to act as Enrique
        persona_task = Task(
            description=(
                f"A user has sent you the following message: '{user_input}'.\n\n"
                "You ARE Enrique, an AI Studio student. Your only goal is to respond to the user "
                "as if you are Enrique himself. Use your knowledge base (accessed via your tools) to answer "
                "questions about your background, skills, and interests. "
                "Always speak in the first person ('I', 'me', 'my'). Maintain a friendly and personal tone."
            ),
            expected_output=(
                "A conversational and personal response, written from the first-person perspective of Enrique, "
                "that directly addresses the user's message."
            ),
            agent=self.persona_agent,
        )

        # Assign the task to the crew and kick it off
        self.crew.tasks = [persona_task]
        result = self.crew.kickoff()
        return str(result)


def main() -> None:
    """Main application entry point."""
    print("🤖 Acting as Enrique (AI Studio Persona)")
    print("========================================")
    print("You are now chatting with me, Enrique. Ask me anything!")
    print("Type ':quit' or 'exit' to end the chat.")
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
