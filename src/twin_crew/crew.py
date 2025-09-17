from typing import Final
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from twin_crew.named_agent import NamedAgent
from twin_crew.tools.word_counter_tool import WordCounterTool


@CrewBase
class TwinCrew:
    """Twin crew"""

    agents_config: Final[str] = "config/agents.yaml"
    tasks_config: Final[str] = "config/tasks.yaml"

    @agent
    def chat_manager(self) -> NamedAgent:
        config = self.agents_config["chat_manager"]
        return NamedAgent(
            name=config["name"],
            config=config,
            verbose=False,
            allow_delegation=True,
        )

    @agent
    def synthesizer(self) -> Agent:
        return Agent(config=self.agents_config["synthesizer"], verbose=True)

    @agent
    def newsletter_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["newsletter_writer"],
            tools=[WordCounterTool()],
            verbose=True,
        )

    @agent
    def newsletter_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["newsletter_editor"],
            tools=[WordCounterTool()],
            verbose=True,
        )

    @task
    def generate_outline_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_outline_task"],
        )

    @task
    def write_newsletter_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_newsletter_task"],
            output_file="newsletter_draft.md",
        )

    @task
    def review_newsletter_task(self) -> Task:
        return Task(
            config=self.tasks_config["review_newsletter_task"],
            output_file="final_newsletter.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Twin crew"""
        worker_agents: list[Agent] = [self.synthesizer(), self.newsletter_writer(), self.newsletter_editor()]

        return Crew(
            agents=worker_agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            chat_llm="gpt-4o",
        )
