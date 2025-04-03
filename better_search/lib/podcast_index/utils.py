import re
from typing import List, Optional, Tuple, Dict, Any, Union

from better_search.core.config import settings
from better_search.core.logger import get_logger
from better_search.lib.podcast_index.schemas import (
    TrendingResults,
    SearchResults,
    TrendingFeed,
    SearchFeed,
    PodcastEpisode,
    EpisodesResults,
)

import podcastindex
from bs4 import BeautifulSoup

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
    max_results: int = 1000,
    fulltext: bool = True,
) -> Optional[EpisodesResults]:
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
            return None

        if episodes_raw and isinstance(episodes_raw, dict):
            return EpisodesResults(**episodes_raw)
        return None

    except Exception as e:
        logger.error(f"Error fetching episodes: {e}")
        return None


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


def format_duration(seconds: int) -> str:
    if not seconds:
        return None
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
    return f"{minutes}:{remaining_seconds:02d}"


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

    return clean_text
