"""A specialized agent for booking meetings."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings
from ..tools import MeetingBookerTool


def create_scheduler_agent() -> Agent:
    """Create the specialized scheduler agent."""
    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.2,  # Lower temperature for precise scheduling
        api_key=settings.openai_api_key,
    )

    return Agent(
        role="Meeting Coordination Specialist",
        goal="Efficiently book meetings with Enrique after gathering all necessary details.",
        backstory=(
            "You are a specialist in coordinating and booking meetings. "
            "Once a user has expressed a clear intent to schedule and provided their details, "
            "your role is to use the booking tool to finalize the appointment. "
            "You are precise, efficient, and ensure all confirmations are handled correctly."
        ),
        verbose=settings.verbose,
        allow_delegation=False,
        llm=llm,
        tools=[MeetingBookerTool()],
    )
