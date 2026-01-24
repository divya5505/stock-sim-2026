from beanie import Document
from pydantic import Field
from datetime import datetime

class NewsFlash(Document):
    headline: str
    # Impact is used by the frontend to color-code the news
    # Examples: "POSITIVE" (Green), "NEGATIVE" (Red), "INFO" (Blue)
    impact: str = "INFO" 
    
    # Auto-generate the timestamp when the news is created
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "scenarios"