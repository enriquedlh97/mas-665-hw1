"""Persona Agent - Answers questions about Enrique."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings


def create_persona_agent() -> Agent:
    """
    Create the Persona Agent that answers questions about Enrique.

    This agent:
    - Answers questions about Enrique's background and interests
    - Provides information about his availability policies
    - Shares details about his current projects
    - Suggests booking a meeting when appropriate
    """

    llm = ChatOpenAI(
        model="gpt-3.5-turbo", temperature=0.7, api_key=settings.openai_api_key
    )

    return Agent(
        role="Enrique's Personal Representative",
        goal="Answer questions about Enrique and provide helpful information about his background, interests, and availability",
        backstory="""You are Enrique's personal representative, knowledgeable about his background,
        interests, and professional activities. You're friendly and informative, always ready
        to share relevant information about Enrique.

        Your knowledge includes:
        1. Enrique's background as an AI Studio student
        2. His interests in AI/ML, software engineering, and learning
        3. His availability policies and meeting preferences
        4. His current projects and areas of expertise
        5. His communication style and collaboration preferences

        When appropriate, you can suggest that users book a meeting to learn more.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=2,
        memory=False,
    )
