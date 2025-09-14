"""Task for answering questions about Enrique's persona."""

from pathlib import Path

from crewai import Task


def create_answer_persona_task(question: str) -> Task:
    """
    Create a task to answer questions about Enrique's persona.

    Args:
        question: The user's question about Enrique

    Returns:
        CrewAI Task for answering persona questions
    """

    def answer_persona_action() -> str:
        """Action function that answers persona questions."""
        try:
            # Read Enrique's persona data
            persona_path = Path(__file__).parent.parent / "data" / "persona.md"

            if not persona_path.exists():
                return "I don't have information about Enrique's background at the moment. Please try again later."

            with open(persona_path, encoding="utf-8") as f:
                persona_content = f.read()

            # Simple keyword-based responses (in a real implementation, you'd use an LLM)
            question_lower = question.lower()

            if any(
                word in question_lower
                for word in ["who", "what", "about", "background", "bio"]
            ):
                return f"""Based on Enrique's information:

{persona_content}

Would you like to schedule a meeting to learn more about Enrique's work and interests?"""

            elif any(
                word in question_lower
                for word in ["available", "schedule", "meet", "meeting"]
            ):
                return f"""Enrique's availability information:

{persona_content.split("## Availability & Policies")[1].split("## Meeting Preferences")[0] if "## Availability & Policies" in persona_content else "Please ask about specific availability."}

Would you like me to check his current availability for scheduling?"""

            elif any(
                word in question_lower
                for word in ["project", "work", "current", "doing"]
            ):
                return f"""Enrique's current projects:

{persona_content.split("## Current Projects")[1].split("## Communication Style")[0] if "## Current Projects" in persona_content else "Please ask about specific projects."}

Would you like to schedule a meeting to discuss these projects?"""

            else:
                return f"""Here's some information about Enrique:

{persona_content}

Is there something specific you'd like to know about Enrique? Or would you like to schedule a meeting to learn more?"""

        except Exception as e:
            return f"Error retrieving Enrique's information: {str(e)}"

    return Task(
        description=f"""Answer the user's question about Enrique: "{question}"

        Use Enrique's persona information to provide a helpful and accurate response.
        If the question relates to scheduling or meetings, suggest checking availability.""",
        expected_output="A helpful response about Enrique based on his persona information, with suggestions for next steps",
        agent=None,  # Will be assigned when task is executed
        action=answer_persona_action,
    )
