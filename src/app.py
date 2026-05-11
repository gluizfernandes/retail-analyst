"""Retail Analyst — Malu Doces Chainlit interface."""

from __future__ import annotations

import chainlit as cl

from src.crew.crew import RetailAnalystCrew

WELCOME = """Ola! Sou a assistente de inteligencia de mercado da **Malu Doces**.

Posso responder perguntas como:

- *Quais marcas tiveram maior faturamento?*
- *Como foi a performance na Pascoa comparado ao Natal?*
- *O que os consumidores falam sobre o Kit Kat?*
- *Qual o share da Mondelez no canal farmacia?*
- *Quais tendencias aparecem nas avaliacoes dos consumidores?*

O que voce gostaria de analisar?
"""


@cl.on_chat_start
async def on_chat_start() -> None:
    await cl.Message(content=WELCOME, author="Malu Doces").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    question = message.content.strip()
    if not question:
        return

    loading = cl.Message(content="Analisando... isso pode levar alguns instantes.", author="Malu Doces")
    await loading.send()

    crew = RetailAnalystCrew()
    result = await cl.make_async(crew.crew().kickoff)(inputs={"question": question})

    await loading.remove()

    tasks = result.tasks_output or []

    async with cl.Step(name="SalesAnalyst — The Ledger", type="tool") as step_sql:
        step_sql.input = question
        step_sql.output = tasks[0].raw if len(tasks) > 0 else "Analise SQL concluida."

    async with cl.Step(name="MarketResearcher — The Memory", type="tool") as step_rag:
        step_rag.input = question
        step_rag.output = tasks[1].raw if len(tasks) > 1 else "Busca semantica concluida."

    await cl.Message(content=result.raw, author="Malu Doces").send()
