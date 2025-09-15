"""Task for orchestrating the overall conversation flow."""

from crewai import Task


def create_orchestrate_conversation_task(user_message: str) -> Task:
    """
    Create a task to orchestrate the conversation flow.

    This task analyzes the user's message and delegates to the appropriate specialist agent.
    The orchestrator agent will determine the best agent to handle the request based on
    the user's intent and available specialist agents.

    Args:
        user_message: The user's input message

    Returns:
        CrewAI Task for conversation orchestration
    """
    return Task(
        description=f"""Analyze the user's message and delegate to the appropriate specialist agent.

        User message: "{user_message}"

        Analyze this message to determine the user's intent and delegate to the most
        appropriate specialist agent available in the crew. Consider:

        1. Questions about Enrique's background, interests, or projects → PersonaAgent
        2. Scheduling requests or availability inquiries → SchedulerAgent (when available)
        3. General greetings or unclear requests → PersonaAgent (default)

        Delegate the task to the appropriate specialist agent and provide them with
        clear context about what the user is asking for.""",
        expected_output=(
            "A clear delegation to the appropriate specialist agent with context about "
            "the user's intent and what they're asking for. The delegated agent should "
            "provide a helpful response that addresses the user's request."
        ),
        agent=None,  # Will be assigned when task is executed
    )
