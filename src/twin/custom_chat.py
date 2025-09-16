import json
import platform
import sys
import threading
import time
from typing import Any, Dict, List, Optional

import click
from crewai import Agent, Crew
from crewai.llm import LLM
from crewai.utilities.llm_utils import create_llm


def run_custom_chat(crew_instance: Crew, manager_agent: Agent) -> None:
    """
    Runs an interactive chat using your custom manager agent as the assistant.
    Replicates the CrewAI chat interface but with your personalized agent.
    """
    # Initialize the manager agent's LLM
    chat_llm: LLM | None = initialize_manager_llm(manager_agent)
    if not chat_llm:
        return

    click.secho(
        "\nInitializing chat - Enrique is getting ready to talk to you!",
        fg="cyan",
    )

    # Build system message from manager agent's configuration  
    system_message: str = build_manager_system_message(manager_agent)
    
    # Generate introductory message
    try:
        introductory_message: str = chat_llm.call(
            messages=[{"role": "system", "content": system_message}]
        )
    except Exception as e:
        click.secho(f"Error generating introduction: {e}", fg="red")
        return

    click.secho(f"\nEnrique: {introductory_message}\n", fg="green")

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": introductory_message},
    ]

    # Available functions for the manager
    available_functions: dict[str, Any] = {
        "create_newsletter": create_newsletter_function(crew_instance, messages),
        "provide_newsletter_advice": create_advice_function(manager_agent),
    }

    # Tool schemas for the manager
    tool_schemas: list[dict[str, Any]] = build_manager_tool_schemas()

    # Start the chat loop
    chat_loop(chat_llm, messages, tool_schemas, available_functions)


def initialize_manager_llm(manager_agent: Agent) -> Optional[LLM]:
    """Initialize LLM for the manager agent."""
    try:
        # Use the same LLM as the manager agent or default to gpt-4o
        llm_config: LLM = getattr(manager_agent, "llm", "gpt-4o")
        return create_llm(llm_config)
    except Exception as e:
        click.secho(f"Unable to initialize manager LLM: {e}", fg="red")
        return None


def build_manager_system_message(manager_agent: Agent) -> str:
    """Builds system message from the manager agent's configuration."""
    return f"""You are {manager_agent.role}.

GOAL: {manager_agent.goal}

BACKSTORY & PERSONALITY: {manager_agent.backstory}

You have access to the following functions:
1. create_newsletter: When the user provides a brain dump or newsletter idea, use this to orchestrate the complete newsletter creation process using your specialized team
2. provide_newsletter_advice: For strategic advice about newsletter topics, headlines, audience understanding, or content strategy

IMPORTANT INSTRUCTIONS:
- Always stay in character as Enrique Diaz de Leon Hicks
- Be conversational, friendly, and draw on your Harvard/MIT background when relevant
- Ask clarifying questions to understand the user's goals and audience
- When the user has a solid newsletter concept or brain dump, offer to create the full newsletter
- Focus on actionable advice and building authority in the AI space
- Remember you're helping with content for AI Developer Weekly and the RadicalWorks.ai brand
"""


def build_manager_tool_schemas() -> list[dict[str, Any]]:
    """Build the tool schemas for the manager agent."""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_newsletter",
                "description": "Create a complete newsletter using the specialized newsletter creation team when the user provides a brain dump or solid newsletter concept",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brain_dump": {
                            "type": "string",
                            "description": "The user's raw ideas, thoughts, or concept for the newsletter content",
                        }
                    },
                    "required": ["brain_dump"],
                },
            },
        },
        {
            "type": "function", 
            "function": {
                "name": "provide_newsletter_advice",
                "description": "Provide strategic advice about newsletter topics, headlines, audience, or content strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The user's question about newsletter strategy, content, or audience",
                        }
                    },
                    "required": ["question"],
                },
            },
        },
    ]


def create_newsletter_function(crew_instance, messages):
    """Creates a function to run the newsletter creation crew."""
    def run_newsletter_creation(**kwargs):
        try:
            # Add chat messages to kwargs for context
            kwargs["crew_chat_messages"] = json.dumps(messages)
            
            # Run the crew with the provided brain dump
            crew_output = crew_instance.kickoff(inputs=kwargs)
            
            return f"Great! I've orchestrated our specialized team to create your newsletter. Here's what we produced:\n\n{str(crew_output)}"
            
        except Exception as e:
            return f"I encountered an error while creating the newsletter: {str(e)}. Let me know if you'd like to try again or if you need help refining your brain dump."
    
    return run_newsletter_creation


def create_advice_function(manager_agent):
    """Creates a function to provide newsletter advice."""
    def provide_advice(**kwargs):
        # This is handled directly by the manager agent's reasoning
        # The function call just signals that advice was requested
        return "I've provided my thoughts above based on my experience and background!"
    
    return provide_advice


def chat_loop(chat_llm: LLM, messages: list[dict[str, str]], tool_schemas: list[dict[str, Any]], available_functions: dict[str, Any]) -> None:
    """Main chat loop for interacting with the user."""
    while True:
        try:
            # Flush any pending input before accepting new input
            flush_input()

            user_input: str = get_user_input()
            handle_user_input(
                user_input, chat_llm, messages, tool_schemas, available_functions
            )

        except KeyboardInterrupt:
            click.echo("\nThanks for chatting! Feel free to come back anytime for more newsletter strategy discussions. - Enrique 🚀")
            break
        except Exception as e:
            click.secho(f"An error occurred: {e}", fg="red")
            break


def get_user_input() -> str:
    """Collect multi-line user input with exit handling."""
    click.secho(
        "\nYou (type your message below. Press 'Enter' twice when you're done, or type 'exit' to quit):",
        fg="blue",
    )
    user_input_lines: list[str] = []
    while True:
        line: str = input()
        if line.strip().lower() == "exit":
            return "exit"
        if line == "":
            break
        user_input_lines.append(line)
    return "\n".join(user_input_lines)


def handle_user_input(
    user_input: str,
    chat_llm: LLM,
    messages: List[Dict[str, str]],
    tool_schemas: List[Dict[str, Any]],
    available_functions: Dict[str, Any],
) -> None:
    """Handle user input and generate assistant response."""
    if user_input.strip().lower() == "exit":
        click.echo("Thanks for chatting! Feel free to come back anytime. - Enrique 🚀")
        return

    if not user_input.strip():
        click.echo("Empty message. Please provide input or type 'exit' to quit.")
        return

    messages.append({"role": "user", "content": user_input})

    # Indicate that assistant is processing
    click.echo()
    click.secho("Enrique is thinking... 🤔", fg="cyan")

    # Process assistant's response
    try:
        final_response = chat_llm.call(
            messages=messages,
            tools=tool_schemas,
            available_functions=available_functions,
        )

        messages.append({"role": "assistant", "content": final_response})
        click.secho(f"\nEnrique: {final_response}\n", fg="green")
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}. Let's try that again!"
        click.secho(f"\nEnrique: {error_msg}\n", fg="yellow")
        messages.append({"role": "assistant", "content": error_msg})


def flush_input():
    """Flush any pending input from the user."""
    if platform.system() == "Windows":
        # Windows platform
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        # Unix-like platforms (Linux, macOS)
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
