"""Retail Analyst — Ingere reviews JSONL no Qdrant (The Memory)."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

REVIEWS_DIR = PROJECT_ROOT / "gen" / "data"
COLLECTION = os.environ.get("RETAIL_QDRANT_COLLECTION", "chocolate_reviews")
QDRANT_URL = os.environ.get("RETAIL_QDRANT_URL", "http://localhost:6334")
VECTOR_SIZE = 384  # BAAI/bge-small-en-v1.5
BATCH_SIZE = 50


def _build_text(review: dict) -> str:
    marca = review.get("marca_nome", "")
    comentario = review.get("comentario", "")
    sentimento = review.get("sentimento", "")
    canal = review.get("canal_compra", "")
    rating = review.get("rating", "")
    return f"Marca: {marca}. Canal: {canal}. Sentimento: {sentimento}. Rating: {rating}/5. {comentario}"


def ingest(reviews_dir: Path = REVIEWS_DIR) -> None:
    files = sorted(reviews_dir.glob("reviews-chocolate*.jsonl"))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo de reviews encontrado em: {reviews_dir}\n"
            "Rode 'podman-compose up' em gen/ para gerar os dados via ShadowTraffic."
        )

    reviews = []
    for f in files:
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                reviews.append(json.loads(line))
    print(f"Reviews carregadas: {len(reviews)} ({len(files)} arquivos)")

    client = QdrantClient(url=QDRANT_URL)
    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Coleção '{COLLECTION}' criada/recriada.")

    model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    for i in range(0, len(reviews), BATCH_SIZE):
        batch = reviews[i : i + BATCH_SIZE]
        texts = [_build_text(r) for r in batch]
        embeddings = list(model.embed(texts))

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb.tolist(),
                payload={
                    "review_id": r.get("review_id", ""),
                    "sku_id": r.get("sku_id", ""),
                    "marca_nome": r.get("marca_nome", ""),
                    "rating": r.get("rating"),
                    "comentario": r.get("comentario", ""),
                    "sentimento": r.get("sentimento", ""),
                    "canal_compra": r.get("canal_compra", ""),
                },
            )
            for r, emb in zip(batch, embeddings)
        ]

        client.upsert(collection_name=COLLECTION, points=points)
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(points)} reviews inseridas.")

    total = client.get_collection(COLLECTION).points_count
    print(f"\nIngesta concluída. Total na coleção '{COLLECTION}': {total} reviews.")


if __name__ == "__main__":
    ingest()
