import podcastindex

from typing import List, Optional, Tuple, Dict, Any, Union

from better_search.core.config import settings
from better_search.core.logger import get_logger
from better_search.lib.podcast_index.schemas import (
    TrendingResults,
    SearchResults,
    TrendingFeed,
    SearchFeed,
)

logger = get_logger()


def initialize_podcast_index():
    config = {
        "api_key": settings.PODCAST_INDEX_API_KEY,
        "api_secret": settings.PODCAST_INDEX_API_SECRET,
    }

    index = podcastindex.init(config)
    index.timeout = 30
    return index


def get_trending_podcasts(
    index,
    language: Optional[List[str]] = None,
    max_results: int = 50,
    categories: Optional[List[int]] = None,
    not_categories: Optional[List[int]] = None,
    since: Optional[int] = None,
) -> Tuple[Optional[TrendingResults], Optional[Dict[str, Any]]]:
    try:
        trending_raw = index.trendingPodcasts(
            lang=language,
            max=max_results,
            categories=categories,
            not_categories=not_categories,
            since=since,
        )
        return TrendingResults(**trending_raw), trending_raw
    except Exception as e:
        logger.error(f"Error fetching trending podcasts: {e}")
        return None, None


def search_podcasts(
    index, query: str, clean: bool = True, max_results: int = 50
) -> Tuple[Optional[SearchResults], Optional[Dict[str, Any]]]:
    try:
        search_raw = index.search(query, clean=clean)
        return SearchResults(**search_raw), search_raw
    except Exception as e:
        logger.error(f"Error searching podcasts: {e}")
        return None, None


def get_podcast_episodes(
    index,
    podcast: Union[TrendingFeed, SearchFeed],
    max_results: int = 100,
    fulltext: bool = True,
) -> List[Dict[str, Any]]:
    episodes_raw = None

    try:
        if hasattr(podcast, "podcastGuid") and podcast.podcastGuid:
            episodes_raw = index.episodesByPodcastGuid(
                podcast.podcastGuid, max_results=max_results, fulltext=fulltext
            )
            logger.info(f"Retrieved episodes by podcast GUID: {podcast.podcastGuid}")

        elif hasattr(podcast, "itunesId") and podcast.itunesId and not episodes_raw:
            episodes_raw = index.episodesByItunesId(
                podcast.itunesId, max_results=max_results, fulltext=fulltext
            )
            logger.info(f"Retrieved episodes by iTunes ID: {podcast.itunesId}")

        elif hasattr(podcast, "id") and podcast.id and not episodes_raw:
            episodes_raw = index.episodesByFeedId(
                podcast.id, max_results=max_results, fulltext=fulltext
            )
            logger.info(f"Retrieved episodes by feed ID: {podcast.id}")

        else:
            logger.warning(
                f"No episodes found for podcast: {getattr(podcast, 'title', 'Unknown')}"
            )

        return episodes_raw
    except Exception as e:
        logger.error(f"Error fetching episodes: {e}")
        return episodes_raw


def get_podcast_by_feed_url(index, feed_url: str) -> Optional[Dict[str, Any]]:
    try:
        podcast_raw = index.podcastByFeedUrl(feed_url)
        if podcast_raw:
            return podcast_raw["feed"]
        else:
            logger.warning(f"No podcast found for feed URL: {feed_url}")
            return None
    except Exception as e:
        logger.error(f"Error fetching podcast by feed URL: {e}")
        return None
