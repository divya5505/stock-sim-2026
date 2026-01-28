import os
import secrets
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from pydantic import BaseModel
import datetime

# --- MODELS ---
from app.models.trade import Trade
from app.models.team import Team
from app.models.stock import Stock
from app.models.config import MarketStatus

# --- SECURITY SETUP ---
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Checks if the user provided the correct Admin Username and Password.
    Values are read from Environment Variables (DigitalOcean) or default to safe values.
    """
    # 1. Get the "Real" credentials from Environment Variables
    #    (If not set, defaults are "admin" and "admin123")
    correct_user = os.getenv("ADMIN_USERNAME", "admin") 
    correct_password = os.getenv("ADMIN_PASSWORD", "admin123") 

    # 2. Securely compare them (secrets.compare_digest prevents timing attacks)
    is_user_correct = secrets.compare_digest(credentials.username, correct_user)
    is_pass_correct = secrets.compare_digest(credentials.password, correct_password)

    if not (is_user_correct and is_pass_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- APPLY SECURITY TO THE ROUTER ---
# This single line protects EVERY endpoint below.
router = APIRouter(dependencies=[Depends(verify_admin)])

# --- HELPER: GET OR CREATE STATUS DOC ---
async def get_status_doc():
    status = await MarketStatus.find_one()
    if not status:
        status = MarketStatus(is_open=True)
        await status.insert()
    return status

# --- 1. GET ALL TRADES ---
class AdminTradeResponse(BaseModel):
    trade_id: str
    team_id: str
    team_name: str
    ticker: str
    side: str
    quantity: int
    price: float
    dealer_id: Optional[str] = None
    timestamp: datetime.datetime

@router.get("/trades", response_model=List[AdminTradeResponse])
async def get_all_market_trades():
    trades = await Trade.find_all().sort(-Trade.timestamp).to_list()
    teams = await Team.find_all().to_list()
    team_map = {t.team_id: t.name for t in teams}
    
    results = []
    for t in trades:
        results.append({
            "trade_id": str(t.id),
            "team_id": t.team_id,
            "team_name": team_map.get(t.team_id, "Unknown Team"),
            "ticker": t.ticker,
            "side": t.side,
            "quantity": t.quantity,
            "price": t.price,
            "dealer_id": t.dealer_id,
            "timestamp": t.timestamp
        })
    return results

# --- 2. MARKET STATUS CONTROL ---
@router.get("/market/status")
async def get_market_status():
    status_doc = await get_status_doc()
    return {
        "is_open": status_doc.is_open,
        "status": "OPEN" if status_doc.is_open else "CLOSED"
    }

@router.post("/market/open")
async def open_market():
    status_doc = await get_status_doc()
    status_doc.is_open = True
    await status_doc.save()
    return {"message": "Market is now OPEN", "status": "OPEN"}

@router.post("/market/close")
async def close_market():
    status_doc = await get_status_doc()
    status_doc.is_open = False
    await status_doc.save()
    return {"message": "Market is now CLOSED", "status": "CLOSED"}

# --- 3. MARKET RESET ---
@router.post("/market/reset")
async def reset_market():
    # A. Delete All Trades
    await Trade.delete_all()
    
    # B. Reset Stocks
    stocks = await Stock.find_all().to_list()
    for s in stocks:
        s.current_price = s.base_price
        s.previous_price = s.base_price
        s.dealer_inventory = 0
        await s.save()
        
    # C. Reset Teams
    teams = await Team.find_all().to_list()
    for t in teams:
        t.cash_balance = 10000.0
        t.portfolio = []
        await t.save()
        
    return {"message": "Market has been fully reset."}