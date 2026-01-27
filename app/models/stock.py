from beanie import Document
from pydantic import Field
from typing import Optional

class Stock(Document):
    # Field(...) is like { required: true }
    ticker: str = Field(..., unique=True)          # e.g., "VOLT"
    name: str = "Unknown"                          # Default to avoid crashes if missing
    
    # The Core Math Fields
    base_price: float                              # The "Day Open" Price. STATIC.
    previous_price: float = 0.0                    # The price 1 second ago. Used for Trend colors.
    current_price: float                           # The LIVE price. UPDATED by market.py.
    
    dealer_inventory: int = 0                      # I_t (Can be negative)
    sensitivity: float = 0.1                       # k (Price impact factor)
    
    class Settings:
        name = "stocks"  # Collection name in MongoDB