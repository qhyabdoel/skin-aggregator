import time
import asyncio
from typing import List, Dict
from datetime import datetime
from app.core.scraper_base import BaseScraper
from app.schemas.listing import Listing

class SkinportScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self._items_cache: List[Dict] = []
        self._last_update = 0
        self._cache_ttl = 300  # 5 minutes

    @property
    def marketplace_name(self) -> str:
        return "Skinport"

    async def _update_cache(self):
        """
        Fetches the full item list from Skinport if the cache is expired.
        """
        now = time.time()
        if self._items_cache and (now - self._last_update < self._cache_ttl):
            return

        try:
            # Fetch items with app_id 730 (CS2) and currency USD
            # Using params instead of hardcoding in URL for cleaner code
            params = {
                "app_id": 730,
                "currency": "USD",
                "tradable": 0 # Get both tradable and non-tradable
            }
            # Add headers to avoid 406 Not Acceptable and 403 Forbidden
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://skinport.com",
                "Referer": "https://skinport.com/",
                "Accept-Encoding": "gzip, deflate, br"
            }
            response = await self.client.get("https://api.skinport.com/v1/items", params=params, headers=headers)
            
            if response.status_code == 401 or response.status_code == 403:
                # Fallback or error logging - but for now just log
                self.logger.error(f"Skinport API access denied: {response.status_code}")
                return

            response.raise_for_status()
            self._items_cache = response.json()
            self._last_update = now
            self.logger.info(f"Updated Skinport cache with {len(self._items_cache)} items")
            
        except Exception as e:
            self.logger.error(f"Failed to update Skinport cache: {e}")

    async def scrape(self, query: str) -> List[Listing]:
        await self._update_cache()

        if not self._items_cache:
            return []

        listings = []
        query_lower = query.lower()
        
        # Filter items client-side
        # Skinport items list structure:
        # [{"market_hash_name": "...", "currency": "USD", "min_price": 12.34, ...}]
        
        for item in self._items_cache:
            market_hash_name = item.get("market_hash_name", "")
            
            # Simple substring match
            if query_lower not in market_hash_name.lower():
                continue

            # Check if there is a valid price
            min_price = item.get("min_price")
            if min_price is None:
                continue

            # Create listing
            # Skinport specific URL construction
            # spaces in market_hash_name should be replaced or encoded
            
            item_url = f"https://skinport.com/market?search={market_hash_name.replace(' ', '%20')}"

            listings.append(Listing(
                marketplace=self.marketplace_name,
                item_name=market_hash_name,
                price=float(min_price),
                currency=item.get("currency", "USD"),
                url=item_url, # type: ignore - Pydantic will validate this
                last_updated=datetime.fromtimestamp(item.get("updated_at", time.time())) 
                             if "updated_at" in item else datetime.now()
            ))

        return listings
