from qdrant_client import QdrantClient, models
from fastembed.embedding import TextEmbedding
from fastembed.sparse.bm25 import Bm25

from pydantic import BaseModel


class HybridSearchResult(BaseModel):
    podcast_id: int
    episode_id: int
    episode_title: str
    podcast_title: str
    podcast_author: str
    podcast_categoires: list
    sim_score: float


class HybridSearch:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = QdrantClient("http://host.docker.internal:6333")
        self.DENSE_MODEL = TextEmbedding(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.SPARSE_MODEL = Bm25("Qdrant/bm25")

    def search(self, query: str):
        query_dense_vector = next(self.DENSE_MODEL.query_embed(query))
        query_sparse_vector = next(self.SPARSE_MODEL.query_embed(query))

        prefecth = [
            models.Prefetch(
                query=query_dense_vector,
                using="fast-paraphrase-multilingual-minilm-l12-v2",
                limit=40,
            ),
            models.Prefetch(
                query=models.SparseVector(**query_sparse_vector.as_object()),
                using="fast-sparse-bm25",
                limit=40,
            ),
        ]

        result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=prefecth,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=10,
            with_payload=True,
        )

        response = [
            HybridSearchResult(
                podcast_id=r.payload["podcast_id"],
                episode_id=r.payload["episode_id"],
                episode_title=r.payload["document"].split("\n")[1],
                podcast_title=r.payload["podcast_name"],
                podcast_author=r.payload["podcast_author"],
                podcast_categoires=r.payload["podcast_categories"],
                sim_score=r.score,
            )
            for r in result.points
        ]

        return response


if __name__ == "__main__":
    searcher = HybridSearch("episodes_enhanced")
    query = "كيف اقدر القى وظيفة"
    print(searcher.search(query))
