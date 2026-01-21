from fastapi import APIRouter, HTTPException, Body
from app.models.team import Team
from app.models.stock import Stock

router = APIRouter()

# --- 1. ADMIN REGISTRATION ---
@router.post("/register")
async def register_team(team_id: str, name: str, password: str):
    exists = await Team.find_one(Team.team_id == team_id)
    if exists:
        raise HTTPException(status_code=400, detail="Team ID taken")
    
    new_team = Team(team_id=team_id, name=name, password=password)
    await new_team.insert()
    return {"message": f"Team {name} registered"}

# --- 2. TEAM LOGIN ---
@router.post("/login")
async def team_login(team_id: str = Body(), password: str = Body()):
    team = await Team.find_one(Team.team_id == team_id)
    if not team or team.password != password:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    return {
        "status": "success",
        "team_name": team.name,
        "cash": round(team.cash_balance, 2),
        "portfolio": team.portfolio
    }

# --- 3. SMART LEADERBOARD ---
@router.get("/leaderboard")
async def get_leaderboard():
    teams = await Team.find_all().to_list()
    stocks = await Stock.find_all().to_list()
    
    # 1. DEBUG PRINT: Check your terminal when you run this!
    print(f"👀 DEBUG: Database returned {len(teams)} teams.")

    # 2. Get current prices
    price_map = {s.ticker: s.current_price for s in stocks}
    
    leaderboard_data = []
    
    for t in teams:
        # Calculate Stock Value
        stock_value = 0.0
        for item in t.portfolio:
            if item.ticker in price_map:
                current_price = price_map[item.ticker]
                stock_value += item.quantity * current_price
        
        # Total Net Worth = Cash + Stock Assets
        total_net_worth = t.cash_balance + stock_value
        
        leaderboard_data.append({
            "team_id": t.team_id,
            "name": t.name,
            "cash": round(t.cash_balance, 2),
            "stock_value": round(stock_value, 2),
            "total_net_worth": round(total_net_worth, 2)
        })
    
    # Sort by Net Worth (Highest First)
    sorted_teams = sorted(leaderboard_data, key=lambda x: x["total_net_worth"], reverse=True)
    
    return sorted_teams