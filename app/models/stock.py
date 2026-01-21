from beanie import Document
from pydantic import Field
from typing import Optional

class Stock(Document):
    # Field(...) is like { required: true }
    ticker: str = Field(..., unique=True)          # e.g., "VOLT"
    company_name: str                              # e.g., "Volt Energy"
    
    # The Core Math Fields (Dealer Model)
    base_price: float = 100.0                      # S_t (Natural Price)
    dealer_inventory: int = 0                      # I_t (Can be negative)
    sensitivity: float = 0.1                       # k (Price impact factor)
    
    class Settings:
        name = "stocks"  # Collection name in MongoDB

    # The Pricing Formula: P = S - (k * I)
    @property
    def current_price(self) -> float:
        # 1. Calculate the Raw Math Price
        raw_price = self.base_price - (self.sensitivity * self.dealer_inventory)
        
        # 2. Apply Security Floor (Circuit Breaker)
        # Price can never mathematically drop below ₹5.00
        return max(5.0, raw_price)