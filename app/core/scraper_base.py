from abc import ABC, abstractmethod
from typing import List
from app.schemas.listing import Listing
import httpx
import logging

class BaseScraper(ABC):
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def marketplace_name(self) -> str:
        """Return the name of the marketplace."""
        pass

    @abstractmethod
    async def scrape(self, query: str) -> List[Listing]:
        """
        Each marketplace implementation must override this.
        It should handle its own HTML parsing and return List[Listing].
        """
        pass

    async def safe_scrape(self, query: str) -> List[Listing]:
        """
        A wrapper to handle failures gracefully. If one marketplace
        fails, it logs the error but doesn't crash the entire request.
        """
        try:
            return await self.scrape(query)
        except Exception as e:
            self.logger.error(f"Error scraping {self.marketplace_name}: {e}")
            return []