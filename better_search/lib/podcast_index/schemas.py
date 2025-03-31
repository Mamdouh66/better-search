from pydantic import BaseModel
from typing import Dict, List, Optional, Union


class SearchFeed(BaseModel):
    id: int
    title: str
    url: str
    originalUrl: str
    link: str
    description: Optional[str] = None
    author: Optional[str] = None
    ownerName: str
    image: Optional[str] = None
    artwork: Optional[str] = None
    lastUpdateTime: int
    lastCrawlTime: int
    lastParseTime: int
    inPollingQueue: int
    priority: int
    lastGoodHttpStatusTime: int
    lastHttpStatus: int
    contentType: str
    itunesId: Optional[int] = None
    generator: Optional[str] = None
    language: Optional[str] = None
    type: int
    dead: int
    crawlErrors: int
    parseErrors: int
    categories: Optional[Dict] = None
    locked: int
    explicit: bool
    podcastGuid: Optional[str] = None
    medium: str
    episodeCount: int
    imageUrlHash: Optional[int] = None
    newestItemPubdate: int


class TrendingFeed(BaseModel):
    id: int
    url: str
    title: str
    description: str
    author: str
    image: str
    artwork: str
    newestItemPublishTime: int
    itunesId: Optional[int] = None
    trendScore: int
    language: str
    categories: Dict[str, str]


class PodcastEpisode(BaseModel):
    id: int
    title: str
    link: str
    description: str
    guid: str
    datePublished: int
    datePublishedPretty: str
    dateCrawled: int
    enclosureUrl: str
    enclosureType: str
    enclosureLength: int
    duration: int
    explicit: int
    episode: Optional[int] = None
    episodeType: Optional[str] = None
    season: Optional[int] = None
    image: Optional[str] = None
    feedItunesId: Optional[int] = None
    feedUrl: Optional[str] = None
    feedImage: Optional[str] = None
    feedId: Optional[int] = None
    podcastGuid: Optional[str] = None
    feedLanguage: Optional[str] = None
    feedDead: Optional[int] = None
    feedDuplicateOf: Optional[int] = None
    chaptersUrl: Optional[str] = None
    transcriptUrl: Optional[str] = None


class EpisodesResults(BaseModel):
    status: str
    items: list[PodcastEpisode]
    count: int
    query: Optional[int]
    description: Optional[str]


class SearchResults(BaseModel):
    status: str
    feeds: List[SearchFeed]
    count: int
    query: str
    description: str


class TrendingResults(BaseModel):
    status: str
    feeds: List[TrendingFeed]
    count: int
    max: int
    since: str
    description: str
