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

def calculate_scores(listings: List[Listing]) -> List[Listing]:
    if not listings: return []
    
    for item in listings:
        # Scoring: (1 / Price) * Freshness factor
        # Higher is better. 
        # We cap price at 1 to avoid division by zero.
        price_factor = 1000 / max(item.price, 1)
        item.raw_score = round(price_factor, 2)
        
    # Sort by score descending (Best deal first)
    return sorted(listings, key=lambda x: x.raw_score, reverse=True)