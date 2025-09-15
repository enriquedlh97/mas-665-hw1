"""Enrique Crew AI System - Simplified and following best practices."""

from .agents.assistant_agent import create_assistant_agent
from .agents.scheduler_agent import create_scheduler_agent

__version__ = "3.0.0"
__author__ = "Enrique Diaz de Leon Hicks"

__all__ = [
    "create_assistant_agent",
    "create_scheduler_agent",
]
