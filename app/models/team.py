from beanie import Document
from pydantic import BaseModel, Field
from typing import List

class PortfolioItem(BaseModel):
    ticker: str
    quantity: int
    average_buy_price: float

class Team(Document):
    team_id: str = Field(..., unique=True)
    name: str
    # NEW: Store a simple password/pin for the team to login
    password: str 
    cash_balance: float = 100000.0
    portfolio: List[PortfolioItem] = []

    class Settings:
        name = "teams"

    def get_holding(self, ticker: str) -> int:
        for item in self.portfolio:
            if item.ticker == ticker:
                return item.quantity
        return 0