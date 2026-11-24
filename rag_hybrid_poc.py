import argparse

from app.services.rag_chunk_engine import ChunkRAGEngine
from app.services.rag_engine import (
    EMBEDDING_MODEL,
    RERANK_MODEL,
    RRF_K
)


def display_chunks(title, chunks, score_key):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    for rank, chunk in enumerate(chunks, 1):

        print(f"\nRang : {rank}")
        print("Metier :", chunk["title"])
        print("Point ID :", chunk["point_id"])
        print("Chunk index :", chunk["chunk_index"])
        print("Source :", chunk["source"])
        print("Score :", round(chunk[score_key], 6))
        print("Extrait :", chunk["text"][:400])


def main():

    parser = argparse.ArgumentParser(
        description="PathForge AI - Hybrid RAG PoC"
    )

    parser.add_argument(
        "--query",
        default=(
            "I am skilled in Python, SQL, Power BI "
            "and data visualization. Which occupation "
            "best matches my profile?"
        )
    )

    args = parser.parse_args()

    print("===== PATHFORGE AI - SEANCE 3 =====")
    print("Embedding :", EMBEDDING_MODEL)
    print("CrossEncoder :", RERANK_MODEL)
    print("RRF k :", RRF_K)

    engine = ChunkRAGEngine()

    print("\nQUESTION :", args.query)

    result = engine.search(args.query)

    print("\n===== RETRIEVAL HYBRIDE =====")
    print("Dense :", result["dense_count"])
    print("BM25 :", result["bm25_count"])
    print("RRF :", result["fusion_count"])

    display_chunks(
        "TOP 5 AVANT RERANKING",
        result["before_reranking"][:5],
        "rrf_score"
    )

    display_chunks(
        "TOP 5 APRES RERANKING",
        result["results"],
        "rerank_score"
    )

    print("\nLatence retrieval :", result["total_ms"], "ms")

    print("\nPOC HYBRID RAG OK")


if __name__ == "__main__":
    main()
