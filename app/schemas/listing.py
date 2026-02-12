from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class Listing(BaseModel):
    marketplace: str = Field(..., description="The name of the site (e.g., eBay)")
    item_name: str
    price: float
    currency: str = "USD"
    url: HttpUrl
    last_updated: datetime
    
    # use this for the 'Best Deal' logic later
    raw_score: float = 0.0

    class Config:
        # Ensures that datetime is serialized to ISO format in JSON
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }