"""Enrique Crew AI System - Multi-agent scheduling assistant."""

from .agents.availability_agent import create_availability_agent
from .agents.chat_agent import create_chat_agent
from .agents.persona_agent import create_persona_agent
from .agents.scheduler_agent import create_scheduler_agent

__version__ = "1.0.0"
__author__ = "Enrique Diaz de Leon Hicks"
