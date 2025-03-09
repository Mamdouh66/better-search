from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, ARRAY
from sqlalchemy.orm import relationship
from better_search.db.database import Base


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(512), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    author = Column(String(255))
    image_url = Column(String(512))
    itunesId = Column(Integer, nullable=True)
    podcastGuid = Column(String(255), nullable=True)
    podcastindex_id = Column(Integer, index=True)
    categories = Column(ARRAY(String))

    episodes = relationship(
        "Episode", back_populates="podcast", cascade="all, delete-orphan"
    )


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    guid = Column(String(512), nullable=False, unique=True)
    date_published = Column(DateTime, nullable=True)
    duration = Column(Integer)  # in seconds
    feedItunesId = Column(Integer, nullable=True)
    image = Column(String(512))
    podcastindex_id = Column(Integer, index=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"), nullable=False)

    podcast = relationship("Podcast", back_populates="episodes")
