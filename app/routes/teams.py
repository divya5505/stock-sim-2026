from fastapi import APIRouter, HTTPException, Body
from app.models.team import Team, TeamMember # Import the new class
from pydantic import BaseModel
from typing import List

router = APIRouter()

# 1. DEFINE THE INPUT FORMAT
class TeamRegisterRequest(BaseModel):
    team_id: str            # From "Team Username"
    name: str               # From "Team Name"
    password: str           # From "Team Password"
    members: List[TeamMember] # The list of student details

# 2. THE REGISTRATION ENDPOINT
@router.post("/register")
async def register_team(data: TeamRegisterRequest):
    # Check for duplicates
    existing_team = await Team.find_one(Team.team_id == data.team_id)
    if existing_team:
        raise HTTPException(status_code=400, detail="Team Username already taken")

    # Create the new team
    new_team = Team(
        team_id=data.team_id,
        name=data.name,
        password=data.password,
        members=data.members, # Saves the full list of details
        cash_balance=100000.0,
        portfolio=[]
    )
    
    await new_team.insert()
    
    return {"message": "Team registered successfully", "team_id": data.team_id}

# 3. GET TEAM INFO
@router.get("/{team_id}")
async def get_team(team_id: str):
    team = await Team.find_one(Team.team_id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team