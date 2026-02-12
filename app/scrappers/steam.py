from typing import List
from datetime import datetime
from app.core.scraper_base import BaseScraper
from app.schemas.listing import Listing

class SteamScraper(BaseScraper):
    @property
    def marketplace_name(self) -> str:
        return "Steam"

    async def scrape(self, query: str) -> List[Listing]:
        # Steam's internal search API returns clean JSON
        url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
        
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        
        listings = []
        
        if not data.get("items"):
            return []

        for item in data["items"]:
            try:
                # Steam prices are in cents (e.g., 2999 = $29.99)
                price_info = item.get("price", {})
                raw_price = price_info.get("final", 0) / 100
                
                # If a game is free or has no price, we handle it
                price = float(raw_price) if raw_price > 0 else 0.0
                
                game_id = item["id"]
                link = f"https://store.steampowered.com/app/{game_id}/"

                listings.append(Listing(
                    marketplace=self.marketplace_name,
                    item_name=item["name"],
                    price=price,
                    currency="USD",
                    url=link,
                    last_updated=datetime.now()
                ))
            except (KeyError, ValueError, TypeError):
                continue

        return listings