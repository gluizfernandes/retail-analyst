"""Retail Analyst — CrewAI tools para The Ledger (SQL) e The Memory (semântico)."""

from __future__ import annotations

import os
import time
from pathlib import Path

import psycopg2
from crewai.tools import tool
from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

_embedding_model: TextEmbedding | None = None


def _get_postgres_connection():
    return psycopg2.connect(
        host=os.environ.get("RETAIL_POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("RETAIL_POSTGRES_PORT", 5433)),
        dbname=os.environ.get("RETAIL_POSTGRES_DB", "malu_doces"),
        user=os.environ.get("RETAIL_POSTGRES_USER", "malu_doces"),
        password=os.environ.get("RETAIL_POSTGRES_PASSWORD", "malu_doces"),
    )


def _get_embedding_model() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _embedding_model


@tool("postgres_execute_sql")
def postgres_execute_sql(query: str) -> str:
    """Execute uma query SQL no banco malu_doces (The Ledger).
    Use para métricas exatas: faturamento, ranking de marcas, share, sazonalidade, canais.
    Tabelas disponíveis: marcas, skus, lojas, vendas.
    IMPORTANTE: a coluna vendas.periodo é VARCHAR(10) no formato 'YYYY-MM'.
    Para extrair o mês use: SUBSTRING(periodo, 6, 2)::integer
    Para extrair o ano use: SUBSTRING(periodo, 1, 4)::integer
    NUNCA use EXTRACT() ou DATE_TRUNC() nessa coluna.
    Escreva apenas SELECT. Nunca execute INSERT, UPDATE ou DELETE."""
    t0 = time.perf_counter()
    conn = _get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        lines = [" | ".join(columns)]
        for row in rows:
            lines.append(" | ".join(str(v) for v in row))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        result = "\n".join(lines)
        return f"{result}\n\n[{len(rows)} linhas — {latency_ms}ms]"
    except Exception as exc:
        return f"SQL Error: {exc}"
    finally:
        conn.close()


@tool("qdrant_semantic_search")
def qdrant_semantic_search(question: str) -> str:
    """Busca semântica em reviews de consumidores de chocolates (The Memory — Qdrant).
    Use para opiniões, sentimentos, reclamações, elogios, tendências e temas de consumo.
    A coleção chocolate_reviews contém reviews em português com: marca, rating, comentário, sentimento, canal_compra."""
    qdrant_url = os.environ.get("RETAIL_QDRANT_URL", "http://localhost:6334")
    collection = os.environ.get("RETAIL_QDRANT_COLLECTION", "chocolate_reviews")

    t0 = time.perf_counter()
    model = _get_embedding_model()
    embeddings = list(model.embed([question]))
    query_vector = embeddings[0].tolist()
    embed_ms = int((time.perf_counter() - t0) * 1000)

    t1 = time.perf_counter()
    client = QdrantClient(url=qdrant_url)
    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=6,
        with_payload=True,
    )
    search_ms = int((time.perf_counter() - t1) * 1000)

    if not results:
        return "Nenhum review encontrado para esta consulta."

    lines: list[str] = []
    for point in results:
        payload = point.payload or {}
        marca = payload.get("marca_nome", "?")
        rating = payload.get("rating", "?")
        sentimento = payload.get("sentimento", "?")
        canal = payload.get("canal_compra", "?")
        comentario = str(payload.get("comentario", ""))[:200]
        score = round(point.score, 3)
        lines.append(
            f"[score={score} | {marca} | rating={rating}/5 | {sentimento} | {canal}]\n  \"{comentario}\""
        )

    return "\n\n".join(lines) + f"\n\n[{len(lines)} reviews — embed {embed_ms}ms | search {search_ms}ms]"
