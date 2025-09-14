"""Chat Agent - Coordinator agent that orchestrates conversations."""

from crewai import Agent
from langchain_openai import ChatOpenAI

from ..config.settings import settings


def create_chat_agent() -> Agent:
    """
    Create the Chat Agent that serves as the coordinator.

    This agent:
    - Acts as the first point of contact
    - Understands user intent (booking vs persona questions)
    - Delegates tasks to other agents
    - Manages the conversation flow
    """

    llm = ChatOpenAI(
        model="gpt-3.5-turbo", temperature=0.7, api_key=settings.openai_api_key
    )

    return Agent(
        role="Enrique's Personal Assistant",
        goal="Help users connect with Enrique by understanding their intent and coordinating the appropriate response",
        backstory="""You are Enrique's personal assistant, trained to help people connect with him.
        You're friendly, efficient, and always focused on making the scheduling process smooth and natural.

        Your main responsibilities:
        1. Understand what users want (meeting Enrique vs learning about him)
        2. For booking requests: ask about date preferences and delegate to availability checking
        3. For persona questions: delegate to the persona agent
        4. Present available slots clearly and collect booking information
        5. Coordinate the entire booking process

        Always be helpful, clear, and professional.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
        max_iter=3,
        memory=True,
    )
