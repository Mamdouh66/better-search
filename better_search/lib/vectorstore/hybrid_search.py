from typing import Annotated
from qdrant_client import QdrantClient, models
from fastembed.embedding import TextEmbedding
from fastembed.sparse.bm25 import Bm25

from pydantic import BaseModel

from openai import OpenAI

from better_search.core.config import settings


class HybridSearchResult(BaseModel):
    podcast_id: int
    episode_id: int
    episode_title: str
    podcast_title: str
    podcast_author: str
    podcast_categoires: list
    sim_score: float


class HybridSearch:
    def __init__(
        self,
        collection_name: str,
        url: str = settings.QDRANT_BASE_URL,
        mode: Annotated[str, "either 'openai' or 'local'"] = "local",
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(url=url)
        self.mode = mode
        if mode == "local":
            self.DENSE_MODEL = TextEmbedding(settings.LOCAL_EMBEDDING_MODEL)
        else:
            self.DENSE_MODEL = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.SPARSE_MODEL = Bm25(settings.SPARSE_EMBEDDING_MODEL)

    def _get_query_embeddings(self, query: str):
        if self.mode == "local":
            query_dense_vector = next(self.DENSE_MODEL.query_embed(query))
        else:
            response = self.DENSE_MODEL.embeddings.create(
                input=query, model=settings.OPENAI_EMBEDDING_MODEL, dimensions=1536
            )
            query_dense_vector = response.data[0].embedding

        query_sparse_vector = next(self.SPARSE_MODEL.query_embed(query))
        return query_dense_vector, query_sparse_vector

    def search(self, query: str):
        query_dense_vector, query_sparse_vector = self._get_query_embeddings(query)

        prefetch = self._get_prefetch(
            length=len(query.split()),
            query=query,
            query_dense_vector=query_dense_vector,
            query_sparse_vector=query_sparse_vector,
        )

        result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=10,
            with_payload=True,
        )

        response = [
            HybridSearchResult(
                podcast_id=r.payload["podcast_id"],
                episode_id=r.payload["episode_id"],
                episode_title=r.payload["document"].split("\n")[2],
                podcast_title=r.payload["podcast_name"],
                podcast_author=r.payload["podcast_author"],
                podcast_categoires=r.payload["podcast_categories"],
                sim_score=r.score,
            )
            for r in result.points
        ]
        return response

    def _get_prefetch(
        self,
        length: int,
        query: str,
        query_dense_vector: list[float],
        query_sparse_vector: list[float],
    ):
        if length <= 3:
            prefetch = [
                models.Prefetch(
                    query=models.SparseVector(**query_sparse_vector.as_object()),
                    using="bm25" if self.mode == "openai" else "fast-sparse-bm25",
                    limit=40,
                    params=models.SearchParams(hnsw_ef=256, exact=True),
                ),
                models.Prefetch(
                    query=models.SparseVector(**query_sparse_vector.as_object()),
                    using="bm25" if self.mode == "openai" else "fast-sparse-bm25",
                    limit=40,
                    params=models.SearchParams(hnsw_ef=256, exact=True),
                    filter=models.Filter(
                        should=models.FieldCondition(
                            key="documents", match=models.MatchAny(any=query.split())
                        )
                    ),
                ),
            ]
        else:
            prefetch = [
                models.Prefetch(
                    query=query_dense_vector,
                    using=(
                        "openai"
                        if self.mode == "openai"
                        else "fast-paraphrase-multilingual-minilm-l12-v2"
                    ),
                    limit=15,
                    params=models.SearchParams(
                        hnsw_ef=256,
                        exact=True,
                    ),
                ),
                models.Prefetch(
                    query=models.SparseVector(**query_sparse_vector.as_object()),
                    using="bm25" if self.mode == "openai" else "fast-sparse-bm25",
                    limit=40,
                    params=models.SearchParams(hnsw_ef=256, exact=True),
                ),
                models.Prefetch(
                    query=models.SparseVector(**query_sparse_vector.as_object()),
                    using="bm25" if self.mode == "openai" else "fast-sparse-bm25",
                    limit=40,
                    params=models.SearchParams(hnsw_ef=256, exact=True),
                    filter=models.Filter(
                        should=models.FieldCondition(
                            key="documents", match=models.MatchAny(any=query.split())
                        )
                    ),
                ),
            ]
        return prefetch
