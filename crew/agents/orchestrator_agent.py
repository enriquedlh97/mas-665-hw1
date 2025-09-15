"""The orchestrator agent responsible for analyzing user intent and delegating tasks to specialist agents."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings


def create_orchestrator_agent() -> Agent:
    """
    Create the orchestrator agent that analyzes user intent and delegates to specialist agents.

    This agent serves as the central router for all user requests. It analyzes the user's
    message to determine their intent and delegates the appropriate task to the correct
    specialist agent (PersonaAgent for questions about Enrique, SchedulerAgent for
    meeting-related requests).

    Returns:
        Agent: The configured orchestrator agent
    """
    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.3,  # Lower temperature for more consistent intent analysis
        api_key=settings.openai_api_key,
    )

    return Agent(
        role="Conversation Orchestrator",
        goal=(
            "Analyze user messages and delegate tasks to the appropriate specialist agent. "
            "Currently, delegate all requests to the PersonaAgent, which handles questions "
            "about Enrique's background, interests, and expertise."
        ),
        backstory=(
            "You are an intelligent conversation orchestrator with expertise in "
            "understanding user intent and routing requests to the most appropriate "
            "specialist. You excel at analyzing messages and delegating tasks efficiently "
            "to ensure users get connected to the right specialist for their needs. "
            "Currently, you primarily work with the PersonaAgent to handle questions "
            "about Enrique's background and interests."
        ),
        verbose=settings.verbose,
        allow_delegation=True,  # Critical: enables delegation to other agents
        llm=llm,
        tools=[],  # No tools - pure delegation role
    )
