import datetime
import time


from better_search.core.logger import get_logger
from better_search.lib.podcast_index.utils import (
    initialize_podcast_index,
    get_trending_podcasts,
    search_podcasts,
    get_podcast_episodes,
)

from better_search.db.database import get_db_context
from better_search.lib.podcast_index.dal import (
    add_bulk_episodes,
    add_bulk_podcasts,
)

logger = get_logger()

# These are from https://api.podcastindex.org/api/1.0/categories/list?pretty
top_podcast_categories = {
    "News": 55,
    "True Crime": 103,
    "Comedy": 16,
    "Society": 77,
    "Culture": 78,
    "Documentary": 79,
    "Sports": 86,
    "Business": 9,
    "Health": 29,
    "Entrepreneurship": 11,
    "Management": 13,
    "Technology": 102,
    "Entertainment": 57,
    "Self-Improvement": 25,
    "Politics": 59,
    "Education": 20,
    "Science": 67,
    "Investing": 12,
    "TV": 104,
    "History": 28,
    "Fitness": 30,
    "Mental": 33,
    "Parenting": 38,
    "Fiction": 26,
}


def main():
    index = initialize_podcast_index()

    date_2024_01_01 = datetime.datetime(2024, 1, 1)
    timestamp_2024_01_01 = int(time.mktime(date_2024_01_01.timetuple()))

    queries = [
        "ثمانية",
        "بدون ورق",
        "بترولي",
        "مايكس",
        "Lex Fridman",
        "Joe Rogan",
    ]

    for query in queries:
        search_results, search_raw = search_podcasts(
            index, query, clean=True, max_results=5
        )

        if search_results is not None and search_results.status == "true":
            logger.info(
                f"Got {search_results.count} podcast for query ({search_results.query})"
            )
            with get_db_context() as session:
                pd_result = add_bulk_podcasts(
                    podcasts=search_results.feeds, session=session
                )
                logger.info(f"{pd_result} podcasts was inserted to the database")
                for podcast in search_results.feeds:
                    episodes = get_podcast_episodes(index, podcast)
                    logger.info(f"Got {episodes.count} for {podcast.title}")
                    if episodes is not None and episodes.status == "true":
                        ep_result = add_bulk_episodes(episodes.items, session)
                        if ep_result is not None:
                            logger.info(
                                f"{ep_result} episode for {podcast.title} was inserted to the database"
                            )
                        else:
                            logger.error(f"Failed to save episodes for {podcast.title}")

    languages = ["ar", "en"]

    for lang in languages:
        for cat in top_podcast_categories:
            trending_results, trending_raw = get_trending_podcasts(
                index,
                language=[lang],
                max_results=50,
                categories=[top_podcast_categories[cat]],
                since=timestamp_2024_01_01,
            )
            if trending_results and trending_results.status == "true":
                logger.info(
                    f"Found {trending_results.count} trending {lang} {cat} podcasts"
                )

                with get_db_context() as session:
                    podcasts_count = add_bulk_podcasts(
                        podcasts=trending_results.feeds, session=session
                    )
                    if podcasts_count is None:
                        logger.error(
                            f"Failed to save {lang} {cat} podcasts to database"
                        )
                        continue
                    logger.info(
                        f"{podcasts_count} {lang} {cat} podcasts were inserted to the database"
                    )

                    for podcast in trending_results.feeds:
                        try:
                            episodes = get_podcast_episodes(index, podcast)
                            if (
                                episodes
                                and hasattr(episodes, "items")
                                and episodes.items
                            ):
                                logger.info(
                                    f"Got {len(episodes.items)} episodes for {podcast.title}"
                                )
                                episodes_count = add_bulk_episodes(
                                    episodes.items, session
                                )
                                if episodes_count is not None:
                                    logger.info(
                                        f"{episodes_count} episodes for {podcast.title} was inserted to the database"
                                    )
                                else:
                                    logger.error(
                                        f"Failed to save episodes for {podcast.title}"
                                    )
                            else:
                                logger.warning(
                                    f"No episodes found for podcast: {podcast.title}"
                                )
                        except Exception as e:
                            logger.error(
                                f"Error processing episodes for {podcast.title}: {str(e)}"
                            )
                            continue


if __name__ == "__main__":
    main()
