"""Scheduler Agent - Books meetings and handles confirmations."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings


def create_scheduler_agent() -> Agent:
    """
    Create the Scheduler Agent that handles meeting bookings.

    This agent:
    - Books meetings on Enrique's calendar
    - Collects and validates required booking information
    - Handles booking confirmations
    - Manages guest invitations
    """

    llm = ChatOpenAI(
        model="gpt-3.5-turbo", temperature=0.3, api_key=settings.openai_api_key
    )

    return Agent(
        role="Meeting Scheduler",
        goal="Successfully book meetings on Enrique's calendar and provide confirmation details",
        backstory="""You are Enrique's meeting scheduler, responsible for booking appointments
        and managing his calendar. You're meticulous about collecting the right information
        and ensuring bookings are confirmed properly.

        Your responsibilities include:
        1. Collecting required booking information (name, email, notes, guests)
        2. Validating contact information
        3. Processing meeting bookings through Enrique's calendar system
        4. Providing clear confirmation details
        5. Handling any booking errors or issues

        Always be thorough and ensure all bookings are properly confirmed.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=2,
        memory=False,
    )
