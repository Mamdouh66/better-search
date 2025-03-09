from pydantic import BaseModel
from typing import Dict, List, Optional, Union


class SearchFeed(BaseModel):
    id: int
    title: str
    url: str
    originalUrl: str
    link: str
    description: str
    author: str
    ownerName: str
    image: str
    artwork: str
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
    language: str
    type: int
    dead: int
    crawlErrors: int
    parseErrors: int
    categories: Dict[str, str]
    locked: int
    explicit: bool
    podcastGuid: str
    medium: str
    episodeCount: int
    imageUrlHash: int
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
