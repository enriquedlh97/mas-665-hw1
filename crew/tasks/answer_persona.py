"""Task for answering questions about Enrique's persona."""

from crewai import Task


def create_answer_persona_task(question: str) -> Task:
    """
    Create a task to answer questions about Enrique's persona.

    This task is designed to be executed by the PersonaAgent, which has access
    to Enrique's persona information through the PersonaReaderTool. The agent
    will use its LLM capabilities to provide natural, conversational responses
    about Enrique's background, interests, and current projects.

    Args:
        question: The user's question about Enrique

    Returns:
        CrewAI Task for answering persona questions
    """
    return Task(
        description=f"""Answer the user's question about Enrique: "{question}"

        You are Enrique Diaz de Leon Hicks. Respond to this question as Enrique himself,
        using your knowledge about your background, interests, current projects, and
        expertise. Maintain a personal, conversational tone and speak in first person.

        Use your PersonaReaderTool to access your complete background information if needed.

        If the user asks about scheduling or meetings, acknowledge their interest and
        suggest they work with the scheduling specialist for availability and booking.""",
        expected_output=(
            "A personal, conversational response from Enrique's perspective that directly "
            "answers the user's question about his background, interests, or projects. "
            "The response should be helpful, engaging, and maintain Enrique's personal voice."
        ),
        agent=None,  # Will be assigned to PersonaAgent when task is executed
    )
