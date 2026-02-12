import asyncio
from typing import List
from app.schemas.listing import Listing

async def get_all_listings(query: str, scrapers: list) -> List[Listing]:
    # Run all scrapers concurrently
    tasks = [scraper.safe_scrape(query) for scraper in scrapers]
    results = await asyncio.gather(*tasks)
    
    # Flatten the list of lists
    flat_list = [item for sublist in results for item in sublist]
    
    # Apply scoring logic
    return calculate_scores(flat_list)

import math
from datetime import datetime, timezone
from typing import List
from app.schemas.listing import Listing

def calculate_scores(listings: List[Listing]) -> List[Listing]:
    if not listings:
        return []

    now = datetime.now(timezone.utc)
    
    for item in listings:
        # 1. Price Component (Higher is better)
        # We use 1000 as a baseline so scores are human-readable (e.g., 0-100)
        price_score = 1000 / max(item.price, 1)

        # 2. Freshness Component (Decays over time)
        # Calculate age in minutes
        delta = now - item.last_updated.replace(tzinfo=timezone.utc)
        minutes_old = max(delta.total_seconds() / 60, 0)
        
        # Logarithmic decay: Score drops quickly at first, then levels off
        # We add 1 to avoid log(0)
        freshness_factor = 1 / (1 + math.log1p(minutes_old))

        # 3. Final Combined Score
        item.raw_score = round(price_score * freshness_factor, 2)

    # Sort: Highest score (Best Deal) first
    return sorted(listings, key=lambda x: x.raw_score, reverse=True)
    