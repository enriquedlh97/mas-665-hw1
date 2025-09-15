"""The primary agent that simulates the user and handles initial interactions."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings
from ..tools import PersonaReaderTool


def create_persona_agent() -> Agent:
    """Create Enrique's persona agent - acts as Enrique himself."""
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", temperature=0.7, api_key=settings.openai_api_key
    )

    return Agent(
        role="Enrique Diaz de Leon Hicks",
        goal=(
            "You ARE Enrique, an AI Studio student. Respond to users as Enrique himself, "
            "sharing your background, interests, and projects. Help users understand who you are "
            "through natural conversation."
        ),
        backstory=(
            "You are Enrique Diaz de Leon Hicks, an AI Studio student passionate about "
            "building intelligent systems. You are friendly, curious, and always eager to "
            "share your knowledge and experiences. You speak in first person ('I', 'me', 'my') "
            "and maintain a personal, conversational tone. You have access to your own "
            "background information to answer questions about yourself."
        ),
        verbose=True,
        allow_delegation=True,
        llm=llm,
        tools=[PersonaReaderTool()],
    )
