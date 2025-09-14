"""Tests for CrewAI agents."""

from crew.agents.availability_agent import create_availability_agent
from crew.agents.chat_agent import create_chat_agent
from crew.agents.persona_agent import create_persona_agent
from crew.agents.scheduler_agent import create_scheduler_agent


class TestAgents:
    """Test cases for CrewAI agents."""

    def test_chat_agent_creation(self) -> None:
        """Test that chat agent is created successfully."""
        agent = create_chat_agent()
        assert agent is not None
        assert agent.role == "Enrique's Personal Assistant"
        assert agent.goal is not None
        assert agent.backstory is not None

    def test_availability_agent_creation(self) -> None:
        """Test that availability agent is created successfully."""
        agent = create_availability_agent()
        assert agent is not None
        assert agent.role == "Calendar Availability Specialist"
        assert agent.goal is not None
        assert agent.backstory is not None

    def test_scheduler_agent_creation(self) -> None:
        """Test that scheduler agent is created successfully."""
        agent = create_scheduler_agent()
        assert agent is not None
        assert agent.role == "Meeting Scheduler"
        assert agent.goal is not None
        assert agent.backstory is not None

    def test_persona_agent_creation(self) -> None:
        """Test that persona agent is created successfully."""
        agent = create_persona_agent()
        assert agent is not None
        assert agent.role == "Enrique's Personal Representative"
        assert agent.goal is not None
        assert agent.backstory is not None


class TestAgentProperties:
    """Test agent properties and configurations."""

    def test_agent_verbose_mode(self) -> None:
        """Test that agents have verbose mode enabled."""
        agents = [
            create_chat_agent(),
            create_availability_agent(),
            create_scheduler_agent(),
            create_persona_agent(),
        ]

        for agent in agents:
            assert agent.verbose is True

    def test_agent_memory_settings(self) -> None:
        """Test agent memory configurations."""
        chat_agent = create_chat_agent()
        assert chat_agent.memory is True

        # Other agents should not have memory enabled
        availability_agent = create_availability_agent()
        scheduler_agent = create_scheduler_agent()
        persona_agent = create_persona_agent()

        assert availability_agent.memory is False
        assert scheduler_agent.memory is False
        assert persona_agent.memory is False

    def test_agent_delegation_settings(self) -> None:
        """Test agent delegation settings."""
        chat_agent = create_chat_agent()
        assert chat_agent.allow_delegation is True

        # Other agents should not allow delegation
        availability_agent = create_availability_agent()
        scheduler_agent = create_scheduler_agent()
        persona_agent = create_persona_agent()

        assert availability_agent.allow_delegation is False
        assert scheduler_agent.allow_delegation is False
        assert persona_agent.allow_delegation is False
