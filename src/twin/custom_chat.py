import json
import platform
import re
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Set

import click
from crewai import Agent, Crew
from crewai.llm import LLM, BaseLLM
from crewai.types.crew_chat import ChatInputField, ChatInputs
from crewai.utilities.llm_utils import create_llm


def run_custom_chat(crew_instance: Crew, manager_agent: Optional[Agent]) -> None:
    """
    Generic interactive chat that mirrors crewAI's chat behavior while
    allowing a manager persona and manager-defined LLM when provided.
    """
    chat_llm: Optional[LLM | BaseLLM] = initialize_chat_llm(crew_instance, manager_agent)
    if not chat_llm:
        return

    # Analyze crew to produce dynamic inputs and tool schema
    loading_complete = threading.Event()
    loading_thread = threading.Thread(target=show_loading, args=(loading_complete,))
    loading_thread.start()

    try:
        crew_name: str = crew_instance.__class__.__name__
        chat_inputs: ChatInputs = generate_crew_chat_inputs(crew_instance, crew_name, chat_llm)
        tool_schema: dict = generate_crew_tool_schema(chat_inputs)
        system_message: str = build_system_message(chat_inputs, manager_agent)
        introductory_message: str = chat_llm.call(messages=[{"role": "system", "content": system_message}])
    finally:
        loading_complete.set()
        loading_thread.join()

    # Announce intro in persona voice if available
    speaker_label: str = get_agent_display_name(manager_agent)
    click.secho(f"\n{speaker_label}: {introductory_message}\n", fg="green")

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": introductory_message},
    ]

    # Expose a single callable tool = the crew itself (generic)
    available_functions: Dict[str, Any] = {
        chat_inputs.crew_name: create_tool_function(crew_instance, messages),
    }

    chat_loop(chat_llm, messages, tool_schema, available_functions, speaker_label)


def initialize_chat_llm(crew: Crew, manager_agent: Optional[Agent]) -> Optional[LLM | BaseLLM]:
    """
    Initialize LLM with priority:
    1) manager_agent.llm if provided
    2) crew.chat_llm if set
    3) default "gpt-4o"
    """
    try:
        if manager_agent and getattr(manager_agent, "llm", None):
            return create_llm(getattr(manager_agent, "llm"))
        if getattr(crew, "chat_llm", None):
            return create_llm(getattr(crew, "chat_llm"))
        return create_llm("gpt-4o")
    except Exception as e:
        click.secho(f"Unable to initialize chat LLM: {e}", fg="red")
        return None


def show_loading(event: threading.Event) -> None:
    """Display animated loading dots while processing."""
    click.secho(
        "\nAnalyzing crew and required inputs - this may take a few seconds depending on complexity.",
        fg="white",
    )
    while not event.is_set():
        print(".", end="", flush=True)
        time.sleep(1)
    print()


def build_system_message(chat_inputs: ChatInputs, manager_agent: Optional[Agent]) -> str:
    """
    Persona-first system message if a manager is provided; otherwise neutral,
    but always includes dynamic crew name, description, and required inputs.
    """
    required_fields_str: str = (
        ", ".join(f"{field.name} (desc: {field.description or 'n/a'})" for field in chat_inputs.inputs)
        or "(No required fields detected)"
    )

    if manager_agent:
        return (
            f"You are {manager_agent.role}. "
            f"Your goal: {manager_agent.goal}. "
            f"Backstory: {manager_agent.backstory}\n\n"
            "You assist users with this crew's purpose. "
            "You have a single function (tool) you can call by name once you have all required inputs. "
            f"Those required inputs are: {required_fields_str}. "
            "Do not call the function until you have all required inputs. "
            "Before doing anything else, introduce yourself and explicitly ask the user for the required inputs. "
            "Keep responses concise and friendly. If the user drifts off-topic, provide a brief answer and guide them back to the crew's purpose.\n"
            f"Crew Name: {chat_inputs.crew_name}\n"
            f"Crew Description: {chat_inputs.crew_description}"
        )

    return (
        "You are a helpful AI assistant for the CrewAI platform. "
        "Your primary purpose is to assist users with the crew's specific tasks. "
        "You can answer general questions, but should guide users back to the crew's purpose afterward. "
        "You have a single function (tool) you can call by name once you have all required inputs. "
        f"Those required inputs are: {required_fields_str}. "
        "Do not call the function until you have all required inputs. "
        "Before doing anything else, introduce yourself and explicitly ask the user for the required inputs. "
        "When you have them, call the function. Keep responses concise and friendly. "
        "If a user asks a question outside the crew's scope, provide a brief answer and remind them of the crew's purpose.\n"
        f"Crew Name: {chat_inputs.crew_name}\n"
        f"Crew Description: {chat_inputs.crew_description}"
    )


def create_tool_function(crew: Crew, messages: List[Dict[str, str]]) -> Any:
    """Create a wrapper that runs the crew with the chat transcript included."""
    def run_with_messages(**kwargs):
        return run_crew_tool(crew, messages, **kwargs)
    return run_with_messages


def run_crew_tool(crew: Crew, messages: List[Dict[str, str]], **kwargs) -> str:
    """
    Runs the crew using crew.kickoff(inputs=kwargs) and returns the output as string.
    Mirrors original behavior and includes serialized chat messages for context.
    """
    try:
        kwargs["crew_chat_messages"] = json.dumps(messages)
        crew_output = crew.kickoff(inputs=kwargs)
        return str(crew_output)
    except Exception as e:
        click.secho("An error occurred while running the crew:", fg="red")
        click.secho(str(e), fg="red")
        sys.exit(1)


def chat_loop(
    chat_llm: LLM | BaseLLM,
    messages: List[Dict[str, str]],
    crew_tool_schema: Dict[str, Any],
    available_functions: Dict[str, Any],
    speaker_label: str,
) -> None:
    """Main chat loop for interacting with the user."""
    while True:
        try:
            flush_input()
            user_input: str = get_user_input()
            handle_user_input(
                user_input, chat_llm, messages, crew_tool_schema, available_functions, speaker_label
            )
        except KeyboardInterrupt:
            click.echo("\nExiting chat. Goodbye!")
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
    user_input_lines: List[str] = []
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
    chat_llm: LLM | BaseLLM,
    messages: List[Dict[str, str]],
    crew_tool_schema: Dict[str, Any],
    available_functions: Dict[str, Any],
    speaker_label: str,
) -> None:
    """Handle user input and generate assistant response."""
    if user_input.strip().lower() == "exit":
        click.echo("Exiting chat. Goodbye!")
        return

    if not user_input.strip():
        click.echo("Empty message. Please provide input or type 'exit' to quit.")
        return

    messages.append({"role": "user", "content": user_input})

    click.echo()
    click.secho(f"{speaker_label} is thinking... 🤔", fg="cyan")

    final_response = chat_llm.call(
        messages=messages,
        tools=[crew_tool_schema],
        available_functions=available_functions,
    )

    messages.append({"role": "assistant", "content": final_response})
    click.secho(f"\n{speaker_label}: {final_response}\n", fg="green")


def flush_input() -> None:
    """Flush any pending input from the user."""
    if platform.system() == "Windows":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)


# ---------- Dynamic crew analysis (ported from original) ----------

def get_agent_display_name(manager_agent: Optional[Agent]) -> str:
    """Best-effort extraction of a human-friendly agent name for chat labels."""
    if not manager_agent:
        return "Assistant"
    # Try common name attributes on Agent
    for attr in ["name", "agent_name", "human_name"]:
        value = getattr(manager_agent, attr, None)
        if isinstance(value, str) and value.strip():
            return value
    # Try config dictionary if present
    config = getattr(manager_agent, "config", None)
    if isinstance(config, dict):
        for key in ["name", "agent_name"]:
            value = config.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return "Assistant"

def generate_crew_chat_inputs(crew: Crew, crew_name: str, chat_llm: LLM | BaseLLM) -> ChatInputs:
    """Analyze the crew to construct ChatInputs containing name, description, and input fields."""
    required_inputs: Set[str] = fetch_required_inputs(crew)

    input_fields: List[ChatInputField] = []
    for input_name in required_inputs:
        description = generate_input_description_with_ai(input_name, crew, chat_llm)
        input_fields.append(ChatInputField(name=input_name, description=description))

    crew_description: str = generate_crew_description_with_ai(crew, chat_llm)
    return ChatInputs(crew_name=crew_name, crew_description=crew_description, inputs=input_fields)


def fetch_required_inputs(crew: Crew) -> Set[str]:
    """Extract placeholders from the crew's tasks and agents, e.g., {brain_dump}."""
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    required_inputs: Set[str] = set()

    for task in crew.tasks:
        text = f"{task.description or ''} {task.expected_output or ''}"
        required_inputs.update(placeholder_pattern.findall(text))

    for agent in crew.agents:
        text = f"{agent.role or ''} {agent.goal or ''} {agent.backstory or ''}"
        required_inputs.update(placeholder_pattern.findall(text))

    return required_inputs


def generate_input_description_with_ai(input_name: str, crew: Crew, chat_llm: LLM | BaseLLM) -> str:
    """Generate a concise input description using AI based on crew context (same behavior as original)."""
    context_texts: List[str] = []
    placeholder_pattern = re.compile(r"\{(.+?)\}")

    for task in crew.tasks:
        if f"{{{input_name}}}" in (task.description or "") or f"{{{input_name}}}" in (task.expected_output or ""):
            task_description = placeholder_pattern.sub(lambda m: m.group(1), task.description or "")
            expected_output = placeholder_pattern.sub(lambda m: m.group(1), task.expected_output or "")
            context_texts.append(f"Task Description: {task_description}")
            context_texts.append(f"Expected Output: {expected_output}")

    for agent in crew.agents:
        if (
            f"{{{input_name}}}" in (agent.role or "")
            or f"{{{input_name}}}" in (agent.goal or "")
            or f"{{{input_name}}}" in (agent.backstory or "")
        ):
            agent_role = placeholder_pattern.sub(lambda m: m.group(1), agent.role or "")
            agent_goal = placeholder_pattern.sub(lambda m: m.group(1), agent.goal or "")
            agent_backstory = placeholder_pattern.sub(lambda m: m.group(1), agent.backstory or "")
            context_texts.append(f"Agent Role: {agent_role}")
            context_texts.append(f"Agent Goal: {agent_goal}")
            context_texts.append(f"Agent Backstory: {agent_backstory}")

    context: str = "\n".join(context_texts)
    if not context:
        raise ValueError(f"No context found for input '{input_name}'.")

    prompt: str = (
        f"Based on the following context, write a concise description (15 words or less) of the input '{input_name}'.\n"
        "Provide only the description, without any extra text or labels. Do not include placeholders like '{topic}' in the description.\n"
        "Context:\n"
        f"{context}"
    )
    response: str = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return response.strip()


def generate_crew_description_with_ai(crew: Crew, chat_llm: LLM | BaseLLM) -> str:
    """Generate a short crew description from tasks and agents (same behavior as original)."""
    context_texts: List[str] = []
    placeholder_pattern = re.compile(r"\{(.+?)\}")

    for task in crew.tasks:
        task_description = placeholder_pattern.sub(lambda m: m.group(1), task.description or "")
        expected_output = placeholder_pattern.sub(lambda m: m.group(1), task.expected_output or "")
        context_texts.append(f"Task Description: {task_description}")
        context_texts.append(f"Expected Output: {expected_output}")

    for agent in crew.agents:
        agent_role = placeholder_pattern.sub(lambda m: m.group(1), agent.role or "")
        agent_goal = placeholder_pattern.sub(lambda m: m.group(1), agent.goal or "")
        agent_backstory = placeholder_pattern.sub(lambda m: m.group(1), agent.backstory or "")
        context_texts.append(f"Agent Role: {agent_role}")
        context_texts.append(f"Agent Goal: {agent_goal}")
        context_texts.append(f"Agent Backstory: {agent_backstory}")

    context: str = "\n".join(context_texts)
    if not context:
        raise ValueError("No context found for generating crew description.")

    prompt: str = (
        "Based on the following context, write a concise, action-oriented description (15 words or less) of the crew's purpose.\n"
        "Provide only the description, without any extra text or labels. Do not include placeholders like '{topic}' in the description.\n"
        "Context:\n"
        f"{context}"
    )
    response: str = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return response.strip()


def generate_crew_tool_schema(crew_inputs: ChatInputs) -> dict:
    """Build Littellm 'function' schema for the crew (same shape as original)."""
    properties: Dict[str, Any] = {}
    for field in crew_inputs.inputs:
        properties[field.name] = {
            "type": "string",
            "description": field.description or "No description provided",
        }

    required_fields: List[str] = [field.name for field in crew_inputs.inputs]

    return {
        "type": "function",
        "function": {
            "name": crew_inputs.crew_name,
            "description": crew_inputs.crew_description or "No crew description",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required_fields,
            },
        },
    }

