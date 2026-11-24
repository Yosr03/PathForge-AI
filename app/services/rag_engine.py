
import json
import re
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder


ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "processed" / "esco_documents_clean.json"

COLLECTION = "pathforge_esco_256"
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

RRF_K = 60
CANDIDATES = 20
DENSE_CHUNKS = 300
RERANK_TOP_N = 20
TOP_K = 5


def tokenize(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def build_rerank_text(doc):
    title = doc.get("title", "")
    text = doc.get("text", "")

    description = text.split("Description:", 1)[-1]
    description = description.split("Essential skills:", 1)[0]
    description = description.split("Optional skills:", 1)[0]
    description = description.strip()

    skills = doc.get("essential_skills", [])
    skills_text = ", ".join(skills[:15])

    return (
        f"Occupation: {title}\n"
        f"Description: {description}\n"
        f"Essential skills: {skills_text}"
    )


class RAGEngine:
    def __init__(self):
        print("Chargement du corpus ESCO...")

        with DATA_FILE.open(encoding="utf-8") as f:
            self.documents = json.load(f)

        self.by_uri = {
            doc["id"]: doc
            for doc in self.documents
        }

        print("Construction de BM25...")

        self.bm25 = BM25Okapi([
            tokenize(doc.get("text", ""))
            for doc in self.documents
        ])

        print("Chargement de BGE-M3...")

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
            device="cpu"
        )

        print("Chargement du CrossEncoder...")

        self.reranker = CrossEncoder(
            RERANK_MODEL,
            device="cpu",
            max_length=512
        )

        print("Connexion à Qdrant...")

        self.client = QdrantClient(
            url="http://localhost:6333"
        )

        self.client.get_collection(COLLECTION)

        print("Moteur Hybrid RAG initialisé.")

    def dense_search_details(self, query, timings=None):
        start_embedding = time.perf_counter()
        vector = self.embedding_model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        embedding_ms = (time.perf_counter() - start_embedding) * 1000

        start_qdrant = time.perf_counter()

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
            limit=DENSE_CHUNKS,
            with_payload=True
        )

        qdrant_ms = (time.perf_counter() - start_qdrant) * 1000

        start_deduplication = time.perf_counter()

        results = []
        seen = set()

        for hit in hits:
            payload = hit.payload or {}
            uri = payload.get("occupation_uri")

            if uri and uri not in seen:
                seen.add(uri)

                results.append({
                    "rank": len(results) + 1,
                    "uri": uri,
                    "title": payload.get("title", ""),
                    "point_id": str(hit.id),
                    "chunk_index": payload.get("chunk_index"),
                    "cosine_score": float(hit.score),
                    "source": payload.get("source", ""),
                    "text": payload.get("text", "")
                })

            if len(results) >= CANDIDATES:
                break

        deduplication_ms = (
            time.perf_counter() - start_deduplication
        ) * 1000

        if timings is not None:
            timings.update({
                "embedding": round(embedding_ms, 2),
                "qdrant": round(qdrant_ms, 2),
                "deduplication": round(deduplication_ms, 2)
            })

        return results

    def dense_search(self, query):
        return [
            row["uri"]
            for row in self.dense_search_details(query)
        ]

    def bm25_search(self, query):
        scores = self.bm25.get_scores(tokenize(query))

        indices = sorted(
            range(len(self.documents)),
            key=lambda i: (-float(scores[i]), i)
        )

        return [
            self.documents[i]["id"]
            for i in indices[:CANDIDATES]
            if scores[i] > 0
        ]

    def rrf_fusion(self, dense, sparse):
        fused = {}

        for ranking in (dense, sparse):
            for rank, uri in enumerate(ranking, start=1):
                fused[uri] = (
                    fused.get(uri, 0.0)
                    + 1.0 / (RRF_K + rank)
                )

        return [
            uri
            for uri, score in sorted(
                fused.items(),
                key=lambda item: (-item[1], item[0])
            )
        ]

    def rerank(self, query, hybrid):
        candidates = [
            uri
            for uri in hybrid
            if uri in self.by_uri
        ][:RERANK_TOP_N]

        if not candidates:
            return []

        pairs = [
            (
                query,
                build_rerank_text(self.by_uri[uri])
            )
            for uri in candidates
        ]

        scores = self.reranker.predict(
            pairs,
            batch_size=8,
            show_progress_bar=False
        )

        ranked = sorted(
            zip(candidates, scores),
            key=lambda item: (-float(item[1]), item[0])
        )

        return [
            {
                "uri": uri,
                "title": self.by_uri[uri]["title"],
                "rerank_score": float(score),
                "text": self.by_uri[uri].get("text", "")
            }
            for uri, score in ranked[:TOP_K]
        ]

    def search(self, query):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("La question ne doit pas être vide.")

        start_total = time.perf_counter()

        dense_timings = {}

        def run_dense():
            start = time.perf_counter()

            details = self.dense_search_details(
                query,
                timings=dense_timings
            )

            uris = [row["uri"] for row in details]
            elapsed = (time.perf_counter() - start) * 1000

            return details, uris, elapsed

        def run_sparse():
            start = time.perf_counter()
            uris = self.bm25_search(query)
            elapsed = (time.perf_counter() - start) * 1000

            return uris, elapsed

        start_parallel = time.perf_counter()

        with ThreadPoolExecutor(max_workers=2) as executor:
            dense_future = executor.submit(run_dense)
            sparse_future = executor.submit(run_sparse)

            dense_details, dense, dense_ms = dense_future.result()
            sparse, bm25_ms = sparse_future.result()

        parallel_ms = (
            time.perf_counter() - start_parallel
        ) * 1000

        start = time.perf_counter()
        hybrid = self.rrf_fusion(dense, sparse)
        rrf_ms = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        reranked = self.rerank(query, hybrid)
        rerank_ms = (time.perf_counter() - start) * 1000

        total_ms = (time.perf_counter() - start_total) * 1000

        return {
            "query": query,
            "configuration": {
                "collection": COLLECTION,
                "dense_top_n": CANDIDATES,
                "bm25_top_n": CANDIDATES,
                "rrf_k": RRF_K,
                "rerank_top_n": RERANK_TOP_N,
                "final_top_k": TOP_K
            },
            "dense_results": dense_details,
            "before_reranking": [
                {
                    "uri": uri,
                    "title": self.by_uri[uri]["title"]
                }
                for uri in hybrid[:TOP_K]
                if uri in self.by_uri
            ],
            "results": reranked,
            "timings_ms": {
                "dense": round(dense_ms, 2),
                **dense_timings,
                "bm25": round(bm25_ms, 2),
                "parallel_retrieval": round(parallel_ms, 2),
                "rrf": round(rrf_ms, 2),
                "reranking": round(rerank_ms, 2),
                "total": round(total_ms, 2)
            }
        }
