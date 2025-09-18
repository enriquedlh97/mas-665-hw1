# Enrique Crew AI - Twin Agent System

A sophisticated, persona-driven AI chat system built on `crewAI`. This project provides a generic and extensible framework for creating a conversational agent that helps users craft a compelling startup pitch designed to attract its persona, Enrique, as a potential technical co-founder.

## 🎯 Project Overview

This system has been refactored into a flexible chat application that dynamically builds its capabilities around a configured `crewAI` crew. Instead of a hard-coded multi-agent setup, it now exposes an entire **pitch-crafting crew** as a single, powerful tool to a chat manager agent.

The core of the application is a custom chat orchestrator that:
1.  **Represents a Persona**: The chat is managed by a "manager" agent (e.g., "Enrique"), who drives the conversation's tone and personality.
2.  **Exposes a Crew as a Tool**: It dynamically discovers the inputs required by a `crew` and presents the entire crew's capability as a single function call to the chat LLM.
3.  **Manages Conversation Flow**: It handles user confirmation before executing the crew, provides clear status updates, and uses hidden state messages to ensure the LLM reliably remembers when tasks have been run.

This architecture allows for a clean separation between the conversational interface and the task-execution backbone, making the system both highly capable and easy to maintain.

## 🤖 Architecture: A Chat Manager with a Crew Tool

The current architecture is designed for clarity, reliability, and flexibility.

1.  **Chat Manager Agent (`NamedAgent`)**: The user interacts with a persona-driven agent defined in `src/twin_crew/config/agents.yaml`. This agent's `name`, `role`, and `backstory` are used to craft the system prompt and drive the user experience.

2.  **The Crew as a Single Tool**: The entire `TwinCrew` (defined in `src/twin_crew/crew.py`) is exposed to the Chat Manager as its only tool. The chat orchestrator automatically determines the inputs the crew needs (`crew.inputs`) and builds a tool schema on the fly.

3.  **Custom Chat Orchestrator (`custom_chat.py`)**: This is the heart of the application. It manages the entire conversation lifecycle:
    *   It builds a persona-aware system prompt.
    *   It asks for user confirmation before calling the `crew` tool.
    *   It injects hidden `[state]` messages into the conversation history to let the LLM know a tool call is about to happen and when it has completed.
    *   It generates a polite, model-generated acknowledgment after the tool runs, before showing the final result.

This design makes the system incredibly flexible. You can add or remove agents, tasks, and tools to the `TwinCrew`, and the chat interface will adapt without requiring any code changes.

## ✨ System Capabilities

The system is designed to be a proactive and strategic partner in developing a co-founder pitch.

-   **Proactive Pitch Development**: Enrique (the Chat Manager) proactively asks for the user's startup idea and gathers all necessary details to create a tailored pitch.
-   **Strategic 3-Stage Pitch Generation**: The worker crew executes a sophisticated three-step process:
    1.  **Strategize**: An agent analyzes the idea against Enrique's background to find the perfect co-founder fit.
    2.  **Draft**: A writer transforms the strategy into a persuasive pitch.
    3.  **Refine**: An editor polishes the draft, ensuring it's concise (max 200 words) and impactful.
-   **Automated Background Integration**: Enrique's professional background is automatically and internally passed to the crew, ensuring every pitch is perfectly tailored to his skills and interests without the user needing to provide it.
-   **Clean, Integrated Output**: The final pitch is delivered directly in the chat as a clean string, with no messy file outputs or markdown blocks.

### Runtime Flow
1.  The chat starts, building the Chat Manager agent from YAML configuration.
2.  The system inspects the `TwinCrew` to determine its required inputs (e.g., `startup_idea`).
3.  A dynamic tool schema is created for the `TwinCrew` function.
4.  The user interacts with the Chat Manager.
5.  If the user's request requires the `TwinCrew`, the manager will ask for confirmation.
6.  Upon confirmation, the `crew.kickoff()` method is executed with the necessary inputs.
7.  The result is returned to the user in a clean, human-readable format.

## 🚀 Quick Start

This project no longer uses Docker or Makefiles. It is now a standard Python project managed with `hatch` and `uv` (or `pip`).

### 1. Prerequisites
- Python 3.11+
- An OpenAI API key

### 2. Installation
Clone the repository and install the dependencies.

```bash
git clone <repository-url>
cd mas-665-hw1

# It is recommended to use a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 3. Configuration
The agent's persona and the crew's tasks are configured via YAML files.

-   **Agent Persona**: Modify `src/twin_crew/config/agents.yaml` to define the Chat Manager's name, role, backstory, and goals.
-   **Crew Tasks**: Modify `src/twin_crew/config/tasks.yaml` to define the tasks that the crew will execute.

You will also need to set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your_key_here"
```

### 4. Running the Chat
The project uses `pyproject.toml` to define convenient scripts. To start the chat interface, run:

```bash
chat
```

This will launch the interactive terminal where you can converse with the agent.

## 🏗️ Project Structure
```
/src/twin_crew/
  config/
    agents.yaml       # Defines the persona of the Chat Manager agent
    tasks.yaml        # Defines the tasks for the worker crew
  tools/
    # Custom tools for the crew can be added here
  crew.py             # Defines the crew, its agents, and tasks
  custom_chat.py      # The core chat orchestration logic
  main.py             # Entry points for the command-line scripts
  named_agent.py      # A custom Agent class with a typed `name` property
```

## Next Steps: Open Questions

The recent refactor has opened up several possibilities for future development:

-   **Multiple Crew Tools**: Should the chat manager be able to access multiple crews or tools at once?
-   **Output Persistence**: Should we store the results of crew runs in a database or file store for later analysis?
-   **"Run Again" Command**: Should there be a shortcut to re-run the last crew execution without needing a second confirmation?

These questions will be explored in future development cycles.
