from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from better_search.lib.podcast_index.models import Podcast, Episode
from better_search.lib.podcast_index.schemas import (
    SearchResults,
    TrendingResults,
    PodcastEpisode,
    SearchFeed,
    TrendingFeed,
)


def add_podcast(podcast: SearchFeed, session: Session):
    try:
        podcast_model = Podcast(
            url=podcast.url,
            title=podcast.title,
            description=podcast.description,
            author=podcast.author,
            image_url=podcast.image,
            itunesId=podcast.itunesId,
            podcastGuid=podcast.podcastGuid,
            podcastindex_id=podcast.id,
            categories=podcast.categories,
        )
        print(f"podcast model is now {podcast_model}")
        session.add(podcast_model)
        session.commit()
        return podcast_model
    except IntegrityError:
        session.rollback()
        return None


def get_existing_podcasts(urls: list[str], session: Session) -> dict:
    query = select(Podcast).where(Podcast.url.in_(urls))
    results = session.execute(query)
    return {podcast.url: podcast for podcast in results.scalars()}


def add_bulk_podcasts(
    podcasts: list[Union[SearchFeed, TrendingFeed]], session: Session
):
    try:
        podcast_urls = [podcast.url for podcast in podcasts]
        existing_podcasts = get_existing_podcasts(podcast_urls, session)

        new_podcasts = [
            podcast for podcast in podcasts if podcast.url not in existing_podcasts
        ]

        if new_podcasts:
            podcasts_model = [
                Podcast(
                    url=podcast.url,
                    title=podcast.title,
                    description=(
                        podcast.description if hasattr(podcast, "description") else None
                    ),
                    author=podcast.author if hasattr(podcast, "author") else None,
                    image_url=podcast.image,
                    itunesId=podcast.itunesId if hasattr(podcast, "itunesId") else None,
                    podcastGuid=(
                        podcast.podcastGuid if hasattr(podcast, "podcastGuid") else None
                    ),
                    podcastindex_id=podcast.id,
                    categories=(
                        list(podcast.categories.values()) if podcast.categories else []
                    ),
                )
                for podcast in new_podcasts
            ]
            session.add_all(podcasts_model)
            session.commit()

        return len(existing_podcasts) + len(new_podcasts)
    except IntegrityError:
        session.rollback()
        return None


def get_podcast_id(podcastindex_id: int, session: Session):
    query = select(Podcast.id).where(Podcast.podcastindex_id == podcastindex_id)
    results = session.execute(query)
    return results.scalar()


def get_existing_episode_guids(guids: list[str], session: Session) -> set[str]:
    query = select(Episode.guid).where(Episode.guid.in_(guids))
    results = session.scalars(query)
    return set(results)


def add_bulk_episodes(episodes: list[PodcastEpisode], session: Session):
    try:
        podcast_id = get_podcast_id(episodes[0].feedId, session)
        if not podcast_id:
            return None

        episode_guids = [episode.guid for episode in episodes]
        existing_guids = get_existing_episode_guids(episode_guids, session)
        new_episodes = [
            episode for episode in episodes if episode.guid not in existing_guids
        ]

        if not new_episodes:
            return 0

        episodes_model = [
            Episode(
                title=episode.title,
                description=episode.description,
                guid=episode.guid,
                date_published=datetime.fromtimestamp(episode.datePublished),
                duration=episode.duration,
                feedItunesId=episode.feedItunesId,
                image=episode.image,
                podcastindex_id=episode.id,
                podcast_id=podcast_id,
            )
            for episode in new_episodes
        ]
        session.add_all(episodes_model)
        session.commit()
        return len(episodes_model)
    except IntegrityError as e:
        print(f"IntegrityError while saving episodes: {str(e)}")
        session.rollback()
        return None
    except Exception as e:
        print(f"Unexpected error while saving episodes: {str(e)}")
        session.rollback()
        return None
