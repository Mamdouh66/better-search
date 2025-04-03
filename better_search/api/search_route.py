from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from better_search.lib.podcast_index.utils import format_duration, clean_description
from better_search.lib.vectorstore.hybrid_search import HybridSearch
from better_search.db.database import get_db
from better_search.lib.podcast_index.models import Episode, Podcast

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

searcher = HybridSearch("episodes_enhanced")


@router.get("/")
def search_podcast(query: str, db: Session = Depends(get_db)):
    search_results = searcher.search(query=query)
    enhanced_results = []

    for result in search_results:
        episode = (
            db.query(Episode)
            .join(Episode.podcast)
            .filter(Episode.id == result.episode_id)
            .first()
        )

        if episode:
            image_url = episode.image if episode.image else episode.podcast.image_url

            enhanced_result = {
                **result.model_dump(),
                "episode_image": image_url,
                "episode_description": clean_description(episode.description) or "",
                "duration_formatted": format_duration(episode.duration),
                "date_published": (
                    episode.date_published.isoformat()
                    if episode.date_published
                    else None
                ),
            }
            enhanced_results.append(enhanced_result)

    return {"result": enhanced_results}
