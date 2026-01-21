from beanie import Document
from pydantic import Field

class Scenario(Document):
    scenario_id: str = Field(..., unique=True) # e.g., "WAR_01"
    headline: str
    ticker: str
    sentiment: float # e.g., 0.25

    class Settings:
        name = "scenarios"