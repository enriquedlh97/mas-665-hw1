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

This project uses `uv` for dependency management and Python environment handling.

### 1. Prerequisites
- **uv**: Install from [https://docs.astral.sh/uv/getting-started/installation/#standalone-installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- **Python 3.11.11**: Tested with Python 3.11.11
- **OpenAI API key**: Required for the chat functionality

### 2. Installation
Clone the repository and install the dependencies using `uv`.

```bash
git clone <repository-url>
cd mas-665-hw1

# Install dependencies and create virtual environment
uv sync
```

This will automatically:
- Create a virtual environment with Python 3.11.11
- Install all project dependencies
- Set up the development environment

### Dependency Management

This project uses `uv` for fast dependency management. The project includes both:
- **`pyproject.toml`**: Primary dependency specification (managed by `uv`)
- **`requirements.txt`**: Generated dependency file for compatibility

**Adding new dependencies:**
```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update requirements.txt after adding dependencies
uv pip freeze > requirements.txt
```

**Note**: Always run `uv pip freeze > requirements.txt` after adding new dependencies via `uv` to keep the requirements.txt file synchronized with your current environment.

### 3. Configuration
The agent's persona and the crew's tasks are configured via YAML files.

-   **Agent Persona**: Modify `src/twin_crew/config/agents.yaml` to define the Chat Manager's name, role, backstory, and goals.
-   **Crew Tasks**: Modify `src/twin_crew/config/tasks.yaml` to define the tasks that the crew will execute.

You will also need to set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your_key_here"
```

### 3. Running the Chat
The project uses `pyproject.toml` to define convenient scripts. To start the chat interface, run:

```bash
chat
```

or if for some reason that files, run
```
uv run chat
```

This will launch the interactive terminal where you can converse with the agent.

## 🏗️ Project Structure
```
/src/twin_crew/
  config/
    agents.yaml       # Defines the persona of the Chat Manager agent
    tasks.yaml        # Defines the tasks for the worker crew
  tools/
    word_counter_tool.py  # Custom tool for enforcing pitch word limits
  crew.py             # Defines the crew, its agents, and tasks
  custom_chat.py      # The core chat orchestration logic
  main.py             # Entry points for the command-line scripts
  named_agent.py      # A custom Agent class with a typed `name` property
```

## 📋 Assignment Documentation

### **Assignment Goal: Digital Twin Lite**
This project fulfills the assignment to "design a simple CrewAI agent that embodies your skills, personality, or interests" by creating Enrique Diaz de Leon Hicks as a digital twin who:

- **Embodies Enrique's Skills**: AI/ML expertise, systems engineering, NLP, and production-grade infrastructure
- **Reflects Enrique's Personality**: Proactive, strategic, collaborative, and focused on agentic systems
- **Handles Tasks on Enrique's Behalf**: Startup pitch strategy, co-founder evaluation, technical positioning, and market analysis


### **Test Results**
**What Worked:**
- ✅ **Persona-Driven Chat**: Enrique's personality and expertise successfully drive conversations
- ✅ **Dynamic Crew Integration**: Seamless exposure of multi-agent crew as single tool
- ✅ **Proactive Behavior**: Enrique actively seeks co-founder opportunities and gathers information
- ✅ **Accurate Word Counting**: Fixed WordCounterTool handles both raw text and escaped JSON inputs
- ✅ **Clean Output**: Direct chat integration without file dependencies

**What Didn't Work Initially:**
- ❌ **CrewAI Chat Limitations**: CrewAI doesn't provide a customizable chat interface beyond `crewai chat` - no way to customize the chatting agent behavior for a good chat experience
- ❌ **Word Count Accuracy**: LLM was passing escaped JSON to WordCounterTool, causing incorrect counts
- ❌ **Background Visibility**: Enrique was showing his background to users instead of passing it internally
- ❌ **Repeated Acknowledgements**: System was acknowledging crew calls on every subsequent message

**What We Learned:**
- **CrewAI Flexibility**: The framework allows for sophisticated multi-agent workflows with clean separation of concerns
- **Persona Integration**: YAML-based agent configuration enables rich, detailed personas that drive authentic interactions
- **Tool Integration**: Custom tools (like WordCounterTool) require careful handling of different input formats
- **Chat Orchestration**: Managing conversation flow with hidden state messages and acknowledgements improves user experience

## 🤖 AI Development Tools Used

### **Cursor AI Assistant**
This project was developed entirely using Cursor. **All code, including this README, was written via prompting Cursor for changes.**

### **Implementation Approach**
The `custom_chat.py` implementation was adapted from CrewAI's built-in chat functionality found in [crew_chat.py](https://github.com/crewAIInc/crewAI/blob/main/src/crewai/cli/crew_chat.py). Rather than reinventing the wheel, we:

- **Leveraged Existing Architecture**: Used CrewAI's proven chat interface as foundation
- **Enhanced with Persona Support**: Added ability to customize manager agent with detailed persona
- **Maintained Compatibility**: Preserved CrewAI's core functionality while adding customization
- **Improved User Experience**: Enhanced conversation flow with acknowledgements and state management

## 🔮 Future Extensions

### **Playwright MCP Integration**
The repository includes a `playwright-mcp` submodule for future iterations that will add MCP (Model Context Protocol) as a tool, enabling web automation capabilities for the agents.

### **Multi-Crew Architecture**
The custom chat implementation is designed to be extended, allowing agents to access multiple crews as tools rather than being limited to a single crew. This will enable more sophisticated workflows and specialized task delegation.
