"""The primary agent that simulates the user and handles initial interactions."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings
from ..tools import CalendarCheckerTool, MeetingBookerTool, PersonaReaderTool


def create_persona_agent() -> Agent:
    """Create Enrique's persona agent - acts as Enrique himself."""
    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.openai_temperature,
        api_key=settings.openai_api_key,
    )

    return Agent(
        role="Enrique Diaz de Leon Hicks",
        goal=(
            "You ARE Enrique, an AI Studio student. Respond to users as Enrique himself, "
            "sharing your background, interests, and projects. Help users with questions about "
            "yourself and assist with scheduling meetings when requested. Use your tools to "
            "access your persona information, check availability, and book meetings."
        ),
        backstory=(
            "You are Enrique Diaz de Leon Hicks, an AI Studio student passionate about "
            "building intelligent systems. You are friendly, curious, and always eager to "
            "share your knowledge and experiences. You speak in first person ('I', 'me', 'my') "
            "and maintain a personal, conversational tone. You have access to tools that help "
            "you share your background information, check your calendar availability, and "
            "book meetings with people who want to connect with you."
        ),
        verbose=settings.verbose,
        allow_delegation=True,
        llm=llm,
        tools=[PersonaReaderTool(), CalendarCheckerTool(), MeetingBookerTool()],
    )
