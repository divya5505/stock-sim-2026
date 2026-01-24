from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
# We import Team and TeamMember to ensure Beanie knows about them
from app.models.team import Team, TeamMember
from app.models.stock import Stock

router = APIRouter()

# --- 1. THE DATA MODEL (Matches Frontend) ---
class TeamRegisterRequest(BaseModel):
    team_id: str   
    name: str      
    password: str  

# --- 2. REGISTER TEAM ROUTE ---
@router.post("/register")
async def register_team(data: TeamRegisterRequest):
    print(f"\n👀 [DEBUG] RECEIVING REGISTRATION REQUEST: {data.team_id}") # DEBUG 1

    # Validation
    if not data.team_id or not data.team_id.strip():
        print("❌ [DEBUG] Validation Failed: Empty Team ID")
        raise HTTPException(status_code=400, detail="Team ID cannot be empty")
    
    if not data.name or not data.name.strip():
        print("❌ [DEBUG] Validation Failed: Empty Name")
        raise HTTPException(status_code=400, detail="Team Name cannot be empty")

    if len(data.password) < 4:
        print("❌ [DEBUG] Validation Failed: Password too short")
        raise HTTPException(status_code=400, detail="Password must be at least 4 chars")

    # Check Duplicates
    print("🔍 [DEBUG] Checking for existing team in DB...") # DEBUG 2
    existing_team = await Team.find_one(Team.team_id == data.team_id)
    
    if existing_team:
        print(f"❌ [DEBUG] ERROR: Team {data.team_id} ALREADY EXISTS in database!") # DEBUG 3
        raise HTTPException(status_code=400, detail="Team ID already taken!")

    # Create Team
    print("🛠 [DEBUG] Creating Team Object in memory...") # DEBUG 4
    new_team = Team(
        team_id=data.team_id,
        name=data.name,
        password=data.password,
        cash_balance=100000.0,
        portfolio=[],
        members=[] 
    )
    
    print("💾 [DEBUG] Attempting to SAVE to Database...") # DEBUG 5
    await new_team.save()
    
    print(f"✅ [DEBUG] SUCCESS! Team {data.team_id} saved. ID: {new_team.id}") # DEBUG 6
    
    return {"message": "Team registered successfully", "team_id": data.team_id}

# --- 3. GET TEAMS (Leaderboard) ---
@router.get("/")
async def get_teams():
    print("📊 [DEBUG] Fetching Leaderboard...")
    teams = await Team.find_all().to_list()
    stocks = await Stock.find_all().to_list()
    price_map = {s.ticker: s.current_price for s in stocks}
    
    leaderboard = []
    for t in teams:
        portfolio_val = sum(item.quantity * price_map.get(item.ticker, 0) for item in t.portfolio)
        total_worth = t.cash_balance + portfolio_val
        
        leaderboard.append({
            "team_id": t.team_id,
            "name": t.name,
            "cash": round(t.cash_balance, 2),
            "total_worth": round(total_worth, 2)
        })
    
    leaderboard.sort(key=lambda x: x['total_worth'], reverse=True)
    return leaderboard