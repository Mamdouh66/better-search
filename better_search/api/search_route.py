from fastapi import APIRouter

from better_search.lib.vectorstore.hybrid_search import HybridSearch


router = APIRouter(
    prefix="/search",
    tags=["search"],
)

searcher = HybridSearch("episodes_enhanced")


@router.get("/")
def search_podcast(query: str):
    return {"result": searcher.search(query=query)}
