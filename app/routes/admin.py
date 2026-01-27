from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import datetime

# --- MODELS ---
from app.models.trade import Trade
from app.models.team import Team
from app.models.stock import Stock
from app.services.market_state import MarketState

router = APIRouter()

# --- 1. GET ALL TRADES (Enriched with Team Names) ---
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
    # 1. Fetch all trades (newest first)
    trades = await Trade.find_all().sort(-Trade.timestamp).to_list()
    
    # 2. Fetch all teams to create a "Lookup Map" (ID -> Name)
    #    This avoids doing N database queries for N trades.
    teams = await Team.find_all().to_list()
    team_map = {t.team_id: t.name for t in teams}
    
    # 3. Build Response
    results = []
    for t in trades:
        results.append({
            "trade_id": str(t.id),
            "team_id": t.team_id,
            "team_name": team_map.get(t.team_id, "Unknown Team"), # Lookup name
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
    return {
        "is_open": MarketState.is_open,
        "status": "OPEN" if MarketState.is_open else "CLOSED"
    }

@router.post("/market/open")
async def open_market():
    MarketState.is_open = True
    return {"message": "Market is now OPEN", "status": "OPEN"}

@router.post("/market/close")
async def close_market():
    MarketState.is_open = False
    return {"message": "Market is now CLOSED", "status": "CLOSED"}

# --- 3. MARKET RESET (The "Big Red Button") ---
@router.post("/market/reset")
async def reset_market():
    """
    WARNING: This wipes all progress.
    1. Deletes all trades.
    2. Resets Stocks to base price & 0 inventory.
    3. Resets Teams to 10k cash & empty portfolio.
    """
    
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
        
    return {"message": "Market has been fully reset. Good luck for the next round!"}