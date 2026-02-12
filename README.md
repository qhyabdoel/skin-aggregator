# Marketplace Scraper API

## Approach

- **Scalability:** Uses the **Strategy Pattern**. Each marketplace is a standalone class.
- **Concurrency:** Leverages `asyncio` to hit all marketplaces at once, reducing latency.
- **Normalization:** Data is strictly validated via **Pydantic** models.
- **Resilience:** `safe_scrape` ensures that if one marketplace fails (404, selector change), the others still return data.

## Adding a New Marketplace

1. Create a new class in `app/scrapers/` (e.g., `walmart.py`).
2. Inherit from `BaseScraper` and implement the `scrape` method.
3. Add the class instance to the `SCRAPERS` list in `app/main.py`.

## Scoring Logic

The "Best Deal" is calculated using a **Value Score**:
$$Score = \frac{1000}{Price}$$
This prioritizes lower prices while the engine preserves data freshness through the 60s cache.
