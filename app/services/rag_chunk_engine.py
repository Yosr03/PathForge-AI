import time
from concurrent.futures import ThreadPoolExecutor

from rank_bm25 import BM25Okapi
from qdrant_client import models

from app.services.rag_engine import (
    RAGEngine,
    tokenize,
    COLLECTION,
    RRF_K,
    CANDIDATES,
    RERANK_TOP_N,
    TOP_K
)


class ChunkRAGEngine:

    def __init__(self, engine=None):

        self.engine = engine if engine is not None else RAGEngine()

        self.client = self.engine.client
        self.embedding_model = self.engine.embedding_model
        self.reranker = self.engine.reranker

        print("Chargement des chunks Qdrant...")

        self.chunks = {}
        offset = None

        while True:

            points, offset = self.client.scroll(
                collection_name=COLLECTION,
                limit=256,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            for point in points:

                payload = point.payload or {}
                pid = str(point.id)

                self.chunks[pid] = {
                    "point_id": pid,
                    "uri": payload["occupation_uri"],
                    "title": payload["title"],
                    "chunk_index": payload["chunk_index"],
                    "text": payload["text"],
                    "source": payload.get("source", "")
                }

            if offset is None:
                break

        self.ids = sorted(self.chunks)

        print("Chunks charges :", len(self.ids))

        print("Construction BM25 sur les chunks...")

        self.bm25 = BM25Okapi([
            tokenize(self.chunks[pid]["text"])
            for pid in self.ids
        ])

        print("CHUNK RAG ENGINE READY")


    def dense_search(self, query):

        vector = self.embedding_model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        hits = self.client.search(
            collection_name=COLLECTION,
            query_vector=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(
                            value="occupation"
                        )
                    )
                ]
            ),
            limit=CANDIDATES,
            with_payload=False
        )

        return [str(hit.id) for hit in hits]


    def bm25_search(self, query):

        scores = self.bm25.get_scores(
            tokenize(query)
        )

        indices = sorted(
            range(len(self.ids)),
            key=lambda i: (-float(scores[i]), i)
        )

        return [
            self.ids[i]
            for i in indices[:CANDIDATES]
            if scores[i] > 0
        ]


    def rrf_fusion(self, dense, sparse):

        fused = {}

        for ranking in (dense, sparse):

            for rank, pid in enumerate(ranking, start=1):

                fused[pid] = (
                    fused.get(pid, 0.0)
                    + 1.0 / (RRF_K + rank)
                )

        ranked = sorted(
            fused.items(),
            key=lambda item: (-item[1], item[0])
        )

        return ranked[:RERANK_TOP_N]


    def rerank(self, query, candidates):

        if not candidates:
            return []

        pairs = [
            (
                query,
                self.chunks[pid]["text"]
            )
            for pid, _ in candidates
        ]

        scores = self.reranker.predict(
            pairs,
            batch_size=8,
            show_progress_bar=False
        )

        ranked = sorted(
            zip(candidates, scores),
            key=lambda item: (
                -float(item[1]),
                item[0][0]
            )
        )

        return [
            {
                **self.chunks[pid],
                "rrf_score": float(rrf_score),
                "rerank_score": float(score)
            }
            for (pid, rrf_score), score in ranked[:TOP_K]
        ]


    def search(self, query):

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Empty query")

        start = time.perf_counter()

        with ThreadPoolExecutor(max_workers=2) as executor:

            dense_future = executor.submit(
                self.dense_search, query
            )

            sparse_future = executor.submit(
                self.bm25_search, query
            )

            dense = dense_future.result()
            sparse = sparse_future.result()

        hybrid = self.rrf_fusion(dense, sparse)

        before = [
            {
                **self.chunks[pid],
                "rrf_score": float(score)
            }
            for pid, score in hybrid
        ]

        after = self.rerank(query, hybrid)

        return {
            "query": query,
            "mode": "chunk",
            "dense_count": len(dense),
            "bm25_count": len(sparse),
            "fusion_count": len(hybrid),
            "before_reranking": before,
            "results": after,
            "total_ms": round(
                (time.perf_counter() - start) * 1000,
                2
            )
        }
