from beanie import Document
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. DEFINE A SINGLE MEMBER
class TeamMember(BaseModel):
    name: str
    email: str
    phone: str
    roll_number: str

# 2. DEFINE PORTFOLIO ITEM (Same as before)
class PortfolioItem(BaseModel):
    ticker: str
    quantity: int
    average_buy_price: float

# 3. THE MAIN TEAM DOCUMENT
class Team(Document):
    team_id: str = Field(..., unique=True) # Maps to "Team Username"
    name: str                              # Maps to "Team Name"
    password: str 
    cash_balance: float = 10000.0
    portfolio: List[PortfolioItem] = []
    
    # NEW: Stores the list of detailed members
    members: List[TeamMember] = []  

    class Settings:
        name = "teams"

    def get_holding(self, ticker: str) -> int:
        for item in self.portfolio:
            if item.ticker == ticker:
                return item.quantity
        return 0