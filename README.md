# Skin Price Aggregator

A simple skin price aggregator for Counter-Strike 2 skins. It fetches prices from multiple marketplaces and identifies the best deals.

## Features

- **Multi-Marketplace Support**: Aggregates listings from multiple marketplaces.
- **Normalization**: returns a standardized JSON format for all listings.
- **Best Deal Logic**: Scores listings based on price and freshness to identify the best deal.
- **Caching**: 
    - Search results are cached for 60 seconds (In-Memory).
    - Skinport full item list is cached for 5 minutes (In-Memory) to respect API rate limits.
- **Resilience**: Gracefully handles individual scraper failures without crashing the entire request.

## Requirements

- Python 3.9+
- `pip`

## Installation

1.  Clone the repository.
2.  Set up a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Start the server:

    ```bash
    uvicorn app.main:app --reload
    ```

2.  Search for a skin:

    You can access the API at `http://localhost:8000/docs#/default/search_search_get`.

    Or use curl:

    ```bash
    curl "http://127.0.0.1:8000/search?q=AK-47"
    ```

## Architecture

-   **`app/main.py`**: FastAPI entry point and caching configuration.
-   **`app/core/engine.py`**: Handles concurrent scraping and listing aggregation/scoring.
-   **`app/core/scraper_base.py`**: Abstract base class that all scrapers must implement.
-   **`app/scrapers/`**: Directory containing specific marketplace implementations (e.g., `steam.py`, `skinport.py`).
-   **`app/schemas/`**: Pydantic models for data validation.

## Adding a New Scraper

1.  Create a new file in `app/scrapers/` (e.g., `buff.py`).
2.  Create a class that inherits from `BaseScraper`.
3.  Implement the `marketplace_name` property and `scrape` method.
4.  Add the new scraper instance to the `SCRAPERS` list in `app/main.py`.
