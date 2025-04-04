from better_search.db.database import get_db_context
from better_search.core.logger import get_logger
from better_search.core.config import settings
from better_search.lib.podcast_index.models import Podcast, Episode

from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from qdrant_client import QdrantClient, models
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import unicodedata
from openai import OpenAI
from fastembed.sparse.bm25 import Bm25


class EpisodeInfo(BaseModel):
    episode_id: int
    title: str
    description: str
    podcast_id: int
    podcast_name: str
    podcast_author: str
    podcast_categories: list


logger = get_logger()


def normalize_arabic(text: str) -> str:
    tashkeel = re.compile(r"[\u0617-\u061A\u064B-\u0652]")
    text = tashkeel.sub("", text)

    text = re.sub("\u0640", "", text)

    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ة", "ه", text)

    text = unicodedata.normalize("NFKC", text)
    return text


def clean_description(text: str) -> str:
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")

    clean_text = soup.get_text(separator=" ", strip=True)

    clean_text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        clean_text,
    )
    clean_text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text)
    clean_text = clean_text.strip()
    clean_text = normalize_arabic(clean_text)

    return clean_text


def get_podcast_with_episodes(ids: list[int], session: Session):
    query = (
        select(
            Episode.title,
            Episode.description,
            Podcast.title.label("podcast_name"),
            Podcast.author.label("podcast_author"),
            Podcast.categories.label("podcast_categories"),
            Podcast.id.label("podcast_id"),
            Episode.id.label("episode_id"),
        )
        .join(
            Podcast,
            Episode.podcast_id == Podcast.id,
        )
        .where(Episode.podcast_id.in_(ids))
    )
    result = session.execute(query)

    episodes_info = [EpisodeInfo(**row._mapping) for row in result]
    return episodes_info


def get_openai_embeddings(texts, batch_size=100):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    embeddings = []

    for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL, input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)

    return embeddings


def handle_local_embeddings(
    qdrant_client: QdrantClient,
    collection_name: str,
    documents: list[str],
    episodes: list[EpisodeInfo],
):
    qdrant_client.set_model(settings.LOCAL_EMBEDDING_MODEL)
    qdrant_client.set_sparse_model(settings.SPARSE_EMBEDDING_MODEL)
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_client.get_fastembed_vector_params(),
            sparse_vectors_config=qdrant_client.get_fastembed_sparse_vector_params(),
        )

    qdrant_client.add(
        collection_name=collection_name,
        documents=documents,
        metadata=[episode.model_dump(exclude={"description"}) for episode in episodes],
        parallel=2,
        ids=tqdm(range(len(documents))),
    )


def handle_openai_embeddings(
    qdrant_client: QdrantClient,
    collection_name: str,
    documents: list[str],
    episodes: list[EpisodeInfo],
):
    SPARSE_MODEL = Bm25(settings.SPARSE_EMBEDDING_MODEL)
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "openai": models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "bm25": models.SparseVectorParams(
                    index=models.SparseIndexParams(
                        on_disk=False,
                    )
                )
            },
        )

    logger.info("Creating sparse vectors with BM25")
    sparse_vectors = []
    for doc in tqdm(documents, desc="Generating sparse vectors"):
        sparse_vector = next(SPARSE_MODEL.embed(doc))
        sparse_vectors.append(sparse_vector)

    logger.info("Generating OpenAI embeddings")
    embeddings = get_openai_embeddings(documents)

    logger.info("Uploading points to Qdrant")
    points = []
    for i, (embedding, episode, doc, sparse_vector) in enumerate(
        zip(embeddings, episodes, documents, sparse_vectors)
    ):
        points.append(
            models.PointStruct(
                id=i,
                vector={
                    "openai": embedding,
                    "bm25": models.SparseVector(**sparse_vector.as_object()),
                },
                payload={
                    "podcast_id": episode.podcast_id,
                    "episode_id": episode.episode_id,
                    "title": episode.title,
                    "podcast_name": episode.podcast_name,
                    "podcast_author": episode.podcast_author,
                    "podcast_categories": episode.podcast_categories,
                    "document": doc,
                },
            )
        )

    batch_size = 100
    for i in tqdm(range(0, len(points), batch_size), desc="Uploading to Qdrant"):
        batch = points[i : i + batch_size]
        qdrant_client.upsert(collection_name=collection_name, wait=True, points=batch)

    logger.info("Embedding ended successfully")


def main(embedding_type: str):
    logger.info("Connecting to qdrant...")
    qdrant_client = QdrantClient(url=settings.QDRANT_BASE_URL)
    collection_name = "podcast_episodes_"
    logger.info("Connected to qdrant")

    podcast_ids = list(range(50, 86)) + list(range(97, 128))
    with get_db_context() as session:
        logger.info(f"Loading episodes from db for {len(podcast_ids)} podcast")
        episodes = get_podcast_with_episodes(podcast_ids, session)
        logger.info(f"Loaded {len(episodes)} episode successfully")

    logger.info("Preparing documents for embedding")
    docs = [
        f"{normalize_arabic(episode.podcast_name)}\n{normalize_arabic(episode.podcast_author)}\n{normalize_arabic(episode.title)}\n{clean_description(episode.description)}"
        for episode in episodes
    ]

    if embedding_type == "local":
        handle_local_embeddings(
            qdrant_client=qdrant_client,
            collection_name=collection_name,
            documents=docs,
            episodes=episodes,
        )
    else:
        handle_openai_embeddings(
            qdrant_client=qdrant_client,
            collection_name=collection_name,
            documents=docs,
            episodes=episodes,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dense",
        choices=["local", "openai"],
        default="openai",
        help="Choose dense embedding type: local or openai",
    )
    args = parser.parse_args()

    main(embedding_type=args.dense)
