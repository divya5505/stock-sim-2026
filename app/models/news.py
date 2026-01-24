from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class NewsFlash(Document):
    headline: str
    
    # Impact: "POSITIVE", "NEGATIVE", "INFO"
    impact: str = "INFO" 
    
    # --- NEW FIELDS ---
    # Default to "MARKET" so general news works
    ticker: str = "MARKET"
    
    # Optional scenario ID for tracking
    scenario_id: Optional[str] = None
    
    # Sentiment Score (e.g., 0.5 for 50% jump, -0.2 for 20% drop)
    # Default is 0.0 (Neutral) to prevent errors with old data
    sentiment: float = 0.0 
    
    # Auto-generate timestamp
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "scenarios"