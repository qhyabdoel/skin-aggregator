from fastapi import FastAPI, Query
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from app.core.engine import get_all_listings
from app.scrapers.skinport import SkinportScraper
from app.scrapers.steam import SteamScraper
from typing import Dict, Any

app = FastAPI(title="Marketplace Aggregator")

# Initialize the scrapers once at startup
SCRAPERS = [SkinportScraper(), SteamScraper()]

@app.on_event("startup")
async def startup():
    # Setup in-memory cache (60s TTL)
    FastAPICache.init(InMemoryBackend())

@app.get("/search")
@cache(expire=60) # This satisfies the 60-second caching requirement
async def search(q: str = Query(..., min_length=2)) -> Dict[str, Any]:
    """
    Search across all marketplaces, normalize data, 
    and identify the best deals.
    """
    all_results = await get_all_listings(q, SCRAPERS)
    
    if not all_results:
        return {"query": q, "total": 0, "results": []}

    # Identify specialized results
    cheapest = min(all_results, key=lambda x: x.price)
    best_deal = max(all_results, key=lambda x: x.raw_score)

    return {
        "query": q,
        "count": len(all_results),
        "best_deal": best_deal,
        "cheapest_listing": cheapest,
        "results": all_results
    }