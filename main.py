"""Main terminal interface for Enrique's Persona AI Agent."""

from crewai import Crew, Process

from crew.agents.orchestrator_agent import create_orchestrator_agent
from crew.agents.persona_agent import create_persona_agent
from crew.config.settings import settings
from crew.tasks.orchestrate_conversation import create_orchestrate_conversation_task


class EnriqueCrewSystem:
    """
    Manages the CrewAI agents and tasks for Enrique's personal AI.

    This system uses an orchestrator-led architecture where the OrchestratorAgent
    analyzes user intent and delegates tasks to appropriate specialist agents.
    Currently active agents:
    - PersonaAgent: Handles questions about Enrique's background and interests

    The architecture is designed to be easily extensible for future specialist agents.
    """

    def __init__(self) -> None:
        """
        Initializes the system by creating the necessary agents.

        The orchestrator agent serves as the central router, while specialist
        agents handle specific domains of functionality. Currently only the
        PersonaAgent is active, but the architecture supports easy addition
        of future specialist agents.
        """
        # Create active agents
        self.orchestrator_agent = create_orchestrator_agent()
        self.persona_agent = create_persona_agent()

        # Future agents can be added here when ready
        # self.scheduler_agent = create_scheduler_agent()

        # Create the Crew with active agents
        self.crew = self._create_crew()

    def _create_crew(self) -> Crew:
        """
        Creates the CrewAI crew with active agents in the orchestrator-led architecture.

        The OrchestratorAgent is listed first as it serves as the primary entry point
        for all user interactions. Additional specialist agents can be easily added
        to this list when they become available.
        """
        return Crew(
            agents=[
                self.orchestrator_agent,  # Primary entry point for all requests
                self.persona_agent,  # Handles persona-related questions
                # Future specialist agents can be added here
                # self.scheduler_agent,     # Handles scheduling and availability
            ],
            tasks=[],
            process=Process.sequential,
            verbose=True,
            memory=True,
        )

    def process_user_input(self, user_input: str) -> str:
        """
        Processes a user's message by creating an orchestration task.

        The OrchestratorAgent analyzes the user's intent and delegates to the
        appropriate specialist agent based on the content of the message.

        Args:
            user_input: The user's message

        Returns:
            str: The response from the appropriate specialist agent
        """
        # Create orchestration task that will analyze intent and delegate appropriately
        orchestration_task = create_orchestrate_conversation_task(user_input)

        # Assign the task to the orchestrator agent
        orchestration_task.agent = self.orchestrator_agent

        # Assign the task to the crew and kick it off
        self.crew.tasks = [orchestration_task]
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
