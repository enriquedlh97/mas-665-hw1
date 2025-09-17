from typing import Optional
from crewai import Agent


class NamedAgent(Agent):
    """Agent with a guaranteed name attribute for type safety."""
    
    name: str
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
