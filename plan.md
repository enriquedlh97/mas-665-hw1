# Architectural Plan: Implementing an Orchestrator Agent

This document outlines the plan to refactor the CrewAI system to be more modular and scalable by introducing an Orchestrator Agent.

## Current State Analysis

The current implementation in `main.py` directly handles user input and assigns tasks to the `PersonaAgent`. This approach is not scalable because it requires hard-coded logic to differentiate between various user intentions (e.g., asking a question vs. booking a meeting). As new functionalities are added, this central logic would become increasingly complex and difficult to maintain.

## Proposed Architecture: The Orchestrator Pattern

To address these limitations, we will adopt an Orchestrator pattern. A new, high-level **Orchestrator Agent** will be introduced to act as a router. Its sole responsibility will be to analyze the user's intent and delegate the task to the appropriate specialist agent.

This architecture will consist of:
1.  **Orchestrator Agent**: The new entry point for all user requests. It determines the user's goal and assigns the task to a specialist.
2.  **Specialist Agents**:
    *   **Persona Agent**: Handles all conversational queries about Enrique's background, skills, and interests.
    *   **Scheduler Agent**: Manages all tasks related to scheduling meetings, such as checking availability and booking appointments via Calendly.

## Implementation Plan

### Step 1: Create the Orchestrator Agent
- Create a new file: `crew/agents/orchestrator_agent.py`.
- Define the `OrchestratorAgent` within this file.
- This agent's `role` will be to analyze user intent. Its `goal` will be to delegate tasks to the correct specialist agent (`Persona` or `Scheduler`).
- The `OrchestratorAgent` will not have any tools itself; its primary function is delegation.

### Step 2: Modularize Tasks
- Move the task definitions out of `main.py` and into dedicated files within the `crew/tasks/` directory.
- **Orchestration Task (`crew/tasks/orchestrate_conversation.py`)**: A new high-level task that takes the user's raw input and is assigned to the `OrchestratorAgent`.
- **Persona Task (`crew/tasks/answer_persona.py`)**: The existing task for answering questions as Enrique. This will be assigned by the `OrchestratorAgent` to the `PersonaAgent`.
- **Scheduling Tasks (`crew/tasks/check_availability.py`, `crew/tasks/book_meeting.py`)**: New tasks for the scheduling flow, which will be assigned by the `OrchestratorAgent` to the `SchedulerAgent`.

### Step 3: Refactor `main.py`
- Modify the `EnriqueCrewSystem` class.
- **Initialization**: In the `__init__` method, initialize all three agents: `OrchestratorAgent`, `PersonaAgent`, and `SchedulerAgent`.
- **Crew Creation**: In the `_create_crew` method, include all three agents in the `agents` list. The `OrchestratorAgent` should be the first in the list, as it will be the entry point.
- **Input Processing**: In the `process_user_input` method, remove the current logic that creates a `persona_task`. Instead, it will create a single `orchestration_task` from `crew/tasks/orchestrate_conversation.py` and assign it to the `OrchestratorAgent`.

## Benefits of This Approach
- **Scalability**: New agents and functionalities can be added with minimal changes to the core application logic. We simply need to teach the Orchestrator about the new specialist.
- **Maintainability**: The code becomes much cleaner and easier to understand, as each component has a single, well-defined responsibility.
- **Alignment with CrewAI Philosophy**: This architecture fully embraces the multi-agent collaboration model that `crewAI` is designed for.

This plan will establish a robust foundation for building a sophisticated and extensible AI assistant.
