from better_search.db.database import get_db_context
from better_search.core.logger import get_logger
from better_search.lib.podcast_index.models import Podcast, Episode

from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from qdrant_client import QdrantClient
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import unicodedata


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

    # Normalize Arabic text
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


def main():
    logger.info("Connecting to qdrant...")
    qdrant_client = QdrantClient(url="http://host.docker.internal:6333")
    logger.info("Connected to qdrant")

    podcast_ids = list(range(50, 86)) + list(range(97, 128))
    with get_db_context() as session:
        logger.info(f"Loading episodes from db for {len(podcast_ids)} podcast")
        episodes = get_podcast_with_episodes(podcast_ids, session)
        logger.info(f"Loaded {len(episodes)} episode successfully")

    qdrant_client.set_model(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    qdrant_client.set_sparse_model("Qdrant/bm25")

    collection_name = "episodes_enhanced"
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_client.get_fastembed_vector_params(),
            sparse_vectors_config=qdrant_client.get_fastembed_sparse_vector_params(),
        )

    logger.info("Embedding episodes into vectorstore")
    docs = [
        f"{normalize_arabic(episode.podcast_name)}\n{normalize_arabic(episode.podcast_author)}\n{normalize_arabic(episode.title)}\n{clean_description(episode.description)}"
        for episode in episodes
    ]

    qdrant_client.add(
        collection_name=collection_name,
        documents=docs,
        metadata=[
            episode.model_dump(exclude={"title", "description"}) for episode in episodes
        ],
        parallel=2,
        ids=tqdm(range(len(docs))),
    )

    logger.info("Embedding ended successfully")


if __name__ == "__main__":
    main()
