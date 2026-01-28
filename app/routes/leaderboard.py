from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from app.models.team import Team
from app.models.stock import Stock

router = APIRouter()

# --- RESPONSE MODEL ---
class LeaderboardEntry(BaseModel):
    rank: int
    team_id: str
    team_name: str
    total_value: float
    cash_balance: float
    portfolio_value: float
    percentage_gain: float

@router.get("/", response_model=List[LeaderboardEntry])
async def get_leaderboard():
    # 1. Fetch all Stocks to create a "Real-Time Price Map"
    #    This prevents us from querying the DB for every single share in every portfolio.
    stocks = await Stock.find_all().to_list()
    price_map = {s.ticker: s.current_price for s in stocks}

    # 2. Fetch all Teams
    teams = await Team.find_all().to_list()

    leaderboard_data = []

    # 3. Calculate Values for each Team
    for team in teams:
        # A. Calculate Portfolio Value (Sum of Quantity * Current Market Price)
        portfolio_value = 0.0
        for item in team.portfolio:
            # If stock ticker missing (deleted?), default price to 0 to avoid crash
            current_price = price_map.get(item.ticker, 0.0) 
            portfolio_value += item.quantity * current_price

        # B. Calculate Total Worth
        total_value = team.cash_balance + portfolio_value

        # C. Calculate Percentage Gain
        # Assuming starting cash is 10,000. 
        # If your starting cash varies, you might want to store 'initial_cash' on the Team model.
        STARTING_CASH = 10000.0
        percentage_gain = ((total_value - STARTING_CASH) / STARTING_CASH) * 100

        leaderboard_data.append({
            "team_id": team.team_id,
            "team_name": team.name,
            "total_value": round(total_value, 2),
            "cash_balance": round(team.cash_balance, 2),
            "portfolio_value": round(portfolio_value, 2),
            "percentage_gain": round(percentage_gain, 2)
        })

    # 4. Sort by Total Value (Highest First)
    leaderboard_data.sort(key=lambda x: x["total_value"], reverse=True)

    # 5. Assign Ranks
    # We rebuild the list to include the "rank" field
    final_leaderboard = []
    for index, entry in enumerate(leaderboard_data):
        entry["rank"] = index + 1
        final_leaderboard.append(entry)

    return final_leaderboard