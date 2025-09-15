"""Enrique Crew AI System - Orchestrator-led architecture."""

from .agents.orchestrator_agent import create_orchestrator_agent
from .agents.persona_agent import create_persona_agent
from .agents.scheduler_agent import create_scheduler_agent

__version__ = "3.0.0"
__author__ = "Enrique Diaz de Leon Hicks"

__all__ = [
    "create_orchestrator_agent",
    "create_persona_agent",
    "create_scheduler_agent",
]
