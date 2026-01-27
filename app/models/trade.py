from beanie import Document
from pydantic import Field
from datetime import datetime
import uuid

class Trade(Document):
    # Auto-generate a unique ID for every trade
    trade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    team_id: str
    ticker: str
    side: str      # "BUY" or "SELL"
    quantity: int
    price: float   # The execution price
    total: float   # Total cost (price * quantity)
    dealer_id: str
    
    # Auto-save the time
    timestamp: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "trades" # Collection name in MongoDB