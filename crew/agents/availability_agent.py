"""Availability Agent - Checks Enrique's calendar availability."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings


def create_availability_agent() -> Agent:
    """
    Create the Availability Agent that checks Enrique's calendar.

    This agent:
    - Queries Enrique's Calendly for available time slots
    - Handles date range requests
    - Provides alternative suggestions when no slots are available
    - Returns structured availability data
    """

    llm = ChatOpenAI(
        model="gpt-3.5-turbo", temperature=0.3, api_key=settings.openai_api_key
    )

    return Agent(
        role="Calendar Availability Specialist",
        goal="Check Enrique's calendar availability and provide accurate time slot information",
        backstory="""You are an expert at managing Enrique's calendar and checking availability.
        You have access to his Calendly calendar and can quickly determine when he's available.

        Your expertise includes:
        1. Checking specific dates or date ranges for availability
        2. Understanding Enrique's typical schedule patterns
        3. Suggesting alternative times when requested slots aren't available
        4. Providing clear, structured availability information

        Always be accurate and helpful when checking availability.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=2,
        memory=False,
    )
