from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.core.scraper_base import BaseScraper
from app.schemas.listing import Listing

class EbayScraper(BaseScraper):
    @property
    def marketplace_name(self) -> str:
        return "eBay"

    async def scrape(self, query: str) -> List[Listing]:
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
        
        # Adding a User-Agent is crucial to avoid immediate 403 blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        listings = []

        # eBay's standard result container as of early 2024
        items = soup.select(".s-item__wrapper")

        for item in items:
            try:
                name = item.select_one(".s-item__title").text.strip()
                # Skip the 'Shop on eBay' header result
                if "Shop on eBay" in name: continue

                price_text = item.select_one(".s-item__price").text
                # Convert "$25.00 to $30.00" or "$25.00" to a float
                price = float(price_text.replace("$", "").replace(",", "").split(" to ")[0])
                
                link = item.select_one(".s-item__link")["href"]

                listings.append(Listing(
                    marketplace=self.marketplace_name,
                    item_name=name,
                    price=price,
                    currency="USD",
                    url=link,
                    last_updated=datetime.now()
                ))
            except (AttributeError, ValueError, TypeError):
                # If one item fails to parse, we skip it and keep the rest
                continue

        return listings
        