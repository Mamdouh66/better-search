from pathlib import Path
from uuid import uuid4

from better_search.core.config import settings

from pydantic import UUID4
from qdrant_client import QdrantClient, models


class VectorStore:
    def __init__(self, client: QdrantClient = None):
        if client:
            self.client = client
        else:
            path = Path().cwd() / "vdb" / "qdrant"
            if path.exists():
                self.client = QdrantClient(path=path)
            else:
                path.mkdir(parents=True)
                self.client = QdrantClient(path=path)

    def create_collection(self, collection_name: str, vector_size: int = 1536):
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                    on_disk=True,
                ),
            )
            print(f"Collection {collection_name} created")
            return True

        print(f"Collection {collection_name} already exists")

    def delete_collection(self, collection_name: str):
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist")
            return

        self.client.delete_collection(collection_name)
        print(f"Collection {collection_name} deleted")

    def insert_vectors(
        self,
        collection_name: str,
        vectors: list[list[float]],
        payload: list[dict] = None,
        ids: list[str] = None,
    ):
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist")
            return

        if not ids:
            ids = [str(uuid4()) for _ in range(len(vectors))]

        points = [
            models.PointStruct(
                id=ids[idx],
                vector=vector,
                payload=payload[idx] if payload else {},
            )
            for idx, vector in enumerate(vectors)
        ]

        self.client.upsert(collection_name=collection_name, points=points)
        print(f"{len(vectors)} Vectors inserted in collection {collection_name}")

    def update_vectors(
        self,
        collection_name: str,
        vectors: list[list[float]],
        payload: list[dict] = None,
        ids: list[str] = None,
    ):
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist")
            return

        if not ids:
            ids = [str(uuid4()) for _ in range(len(vectors))]

        points = [
            models.PointStruct(
                id=ids[idx],
                vector=vector,
                payload=payload[idx] if payload else {},
            )
            for idx, vector in enumerate(vectors)
        ]
        self.client.upsert(
            collection_name=collection_name,
            points=points,
        )
        print(f"{len(vectors)} Vectors updated in collection {collection_name}")

    def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 5,
        filter: dict = None,
    ):
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist")
            return

        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=filter,
        )
        print(
            f"Searched collection {collection_name} and returned {len(search_result)} results"
        )
        return search_result

    def get_vector(self, collection_name: str, vector_id: str):
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist")
            return

        vector = self.client.retrieve(
            collection_name=collection_name, ids=[vector_id], with_payload=True
        )
        print(f"Retrieved vector for {vector_id} from collection {collection_name}")
        return vector[0] if vector else None

    def get_all_vectors(self, collection_name: str, limit: int = 50):
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist")
            return

        all_vectors = self.client.scroll(
            collection_name, limit=limit, with_payload=True, with_vectors=False
        )
        print(f"Retrieved all vectors from collection {collection_name}")
        return all_vectors
