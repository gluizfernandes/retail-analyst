"""Retail Analyst — Malu Doces CrewAI crew (SalesAnalyst + MarketResearcher + Reporter)."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.crew.tools import postgres_execute_sql, qdrant_semantic_search


@CrewBase
class RetailAnalystCrew:
    """Crew de análise de sell-out para o mercado de chocolates."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def sales_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["sales_analyst"],
            tools=[postgres_execute_sql],
            allow_delegation=False,
            llm="groq/llama-3.3-70b-versatile",
            verbose=True,
        )

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_researcher"],
            tools=[qdrant_semantic_search],
            allow_delegation=False,
            llm="groq/llama-3.3-70b-versatile",
            verbose=True,
        )

    @agent
    def reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["reporter"],
            allow_delegation=False,
            llm="groq/llama-3.3-70b-versatile",
            verbose=True,
        )

    @task
    def sales_task(self) -> Task:
        return Task(config=self.tasks_config["sales_task"])

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config["report_task"],
            context=[self.sales_task(), self.research_task()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def run(question: str) -> str:
    result = RetailAnalystCrew().crew().kickoff(inputs={"question": question})
    return result.raw


if __name__ == "__main__":
    question = (
        "Faça uma análise completa do mercado de chocolates: "
        "ranking de marcas por faturamento, meses de maior venda, "
        "performance por canal e o que os consumidores falam sobre as marcas líderes."
    )
    print(run(question))
