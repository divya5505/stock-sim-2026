from beanie import Document
from pydantic import Field

class Dealer(Document):
    username: str = Field(..., unique=True)  # e.g., "DEALER_1"
    password: str                            # e.g., "admin123"
    
    class Settings:
        name = "dealers"