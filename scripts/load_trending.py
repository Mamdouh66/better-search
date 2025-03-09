import json
import datetime
import time
import os


from better_search.lib.podcast_index.utils import (
    initialize_podcast_index,
    get_trending_podcasts,
    search_podcasts,
    get_podcast_episodes,
    get_podcast_by_feed_url,
)

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


def save_to_json(data, filename: str) -> None:
    os.makedirs("tmp", exist_ok=True)
    with open(f"tmp/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to tmp/{filename}")


def main():
    index = initialize_podcast_index()

    date_2024_01_01 = datetime.datetime(2024, 1, 1)
    timestamp_2024_01_01 = int(time.mktime(date_2024_01_01.timetuple()))

    trending_results, trending_raw = get_trending_podcasts(
        index,
        language=["ar"],
        max_results=100,
        categories=[top_podcast_categories["Society"]],
        since=timestamp_2024_01_01,
    )

    search_results, search_raw = search_podcasts(index, "ثمانية", clean=True)

    if trending_results:
        print(
            f"Found {trending_results.count} trending Arabic entrepreneurship podcasts"
        )
        save_to_json(trending_raw, "trending_results.json")

        if trending_results.count > 0:
            first_podcast = trending_results.feeds[0]
            print(f"Getting episodes for: {first_podcast.title}")
            episodes = get_podcast_episodes(index, first_podcast)
            save_to_json(episodes, "first_podcast_episodes.json")

    if search_results:
        print(f"Found {search_results.count} podcasts matching 'سوالف بزنس'")
        save_to_json(search_raw, "search_results.json")

        if search_results.count > 0:
            feed_url = search_results.feeds[0].url
            print(f"Getting podcast details for feed URL: {feed_url}")
            podcast = get_podcast_by_feed_url(index, feed_url)
            if podcast:
                save_to_json(podcast, "podcast_by_feed_url.json")


if __name__ == "__main__":
    main()
