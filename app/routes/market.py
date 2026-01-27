from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List

# --- IMPORTS ---
from app.models.stock import Stock
from app.models.team import Team, PortfolioItem
from app.models.dealer import Dealer
from app.models.trade import Trade 
from app.models.config import MarketStatus

from beanie.operators import Set

router = APIRouter()

# --- CONFIGURATION ---
MAX_SHARES_PER_TEAM = 10000
MIN_PRICE_FLOOR = 5.0      

class DealerLoginRequest(BaseModel):
    username: str
    password: str

# --- 1. DEALER LOGIN ---
@router.post("/dealer/login")
async def dealer_login(data: DealerLoginRequest):
    dealer = await Dealer.find_one(Dealer.username == data.username)
    if not dealer or dealer.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return {"message": "Success", "username": dealer.username, "role": "dealer"}

# --- 2. GET PRICES (FIXED TREND LOGIC) ---
@router.get("/prices")
async def get_prices():
    stocks = await Stock.find_all().to_list()
    
    response_data = []
    
    for s in stocks:
        # LOGIC: Compare Current Price (T) vs Previous Price (T-1)
        # If Current > Previous -> UP (Green)
        # If Current < Previous -> DOWN (Red)
        if s.current_price > s.previous_price:
            trend_direction = "UP"
        elif s.current_price < s.previous_price:
            trend_direction = "DOWN"
        else:
            trend_direction = "FLAT" # No change

        display_name = getattr(s, 'name', s.ticker) 

        response_data.append({
            "ticker": s.ticker,
            "company_name": display_name,
            "current_price": round(s.current_price, 2),
            "base_price": round(s.base_price, 2), # This is now the static "Day Open" price
            "trend": trend_direction
        })
        
    return response_data

# --- 3. EXECUTE TRADE ---
@router.post("/trade")
async def trade_stock(
    team_id: str = Body(),
    ticker: str = Body(),
    quantity: int = Body(),
    side: str = Body(), 
    dealer_id: str = Body(),
    dealer_password: str = Body()
):
    # 1. CHECK MARKET STATUS (Add this at the very top)
    if not MarketStatus.is_open:
        raise HTTPException(status_code=403, detail="Market is currently CLOSED.")
    
    # A. AUTHENTICATE
    dealer = await Dealer.find_one(Dealer.username == dealer_id)
    if not dealer or dealer.password != dealer_password:
        raise HTTPException(status_code=401, detail="Invalid Dealer Credentials")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    stock = await Stock.find_one(Stock.ticker == ticker)
    team = await Team.find_one(Team.team_id == team_id)
       
    if not stock or not team:
        raise HTTPException(status_code=404, detail="Team or Stock not found")

    if side == "sell" and stock.current_price <= MIN_PRICE_FLOOR:
        raise HTTPException(status_code=400, detail="Market Halted: Price too low to sell!")

    if side == "buy":
        current_holding = 0
        for item in team.portfolio:
            if item.ticker == ticker:
                current_holding = item.quantity
                break
        
        if (current_holding + quantity) > MAX_SHARES_PER_TEAM:
             raise HTTPException(status_code=400, detail=f"Limit exceeded for {ticker}")

    # --- B. CALCULATE SLIPPAGE (FIXED) ---
    # 1. Start from the CURRENT price (Last traded price)
    start_price = stock.current_price 
    
    # 2. Calculate impact
    impact = stock.sensitivity * quantity
    
    if side == "buy":
        end_price = start_price + impact
        end_inventory = stock.dealer_inventory - quantity
    else: 
        end_price = start_price - impact
        end_inventory = stock.dealer_inventory + quantity
        
    # 3. Apply Safety Floors
    end_price = max(MIN_PRICE_FLOOR, end_price)
    start_price = max(MIN_PRICE_FLOOR, start_price)
    
    # 4. Average Execution Price
    avg_price = (start_price + end_price) / 2
    total_cost = avg_price * quantity
    
    # --- IMPORTANT UPDATE LOGIC ---
    # 1. Previous Price becomes what Current Price WAS (History)
    # 2. Current Price becomes the NEW End Price (Live)
    # 3. Base Price is UNTOUCHED (It stays as the "Day Open" price)
    await stock.update(Set({
        Stock.previous_price: start_price,  # Save history for trend
        Stock.current_price: end_price,     # Update live price
        Stock.dealer_inventory: end_inventory
    }))

    # --- C. EXECUTE TRANSACTION ---
    if side == "buy":
        if team.cash_balance < total_cost:
            raise HTTPException(status_code=400, detail="Not enough cash!")
        
        team.cash_balance -= total_cost
        
        found = False
        for item in team.portfolio:
            if item.ticker == ticker:
                current_val = item.quantity * item.average_buy_price
                new_val = current_val + total_cost
                new_qty = item.quantity + quantity
                
                item.average_buy_price = new_val / new_qty
                item.quantity = new_qty
                found = True
                break
        
        if not found:
            team.portfolio.append(PortfolioItem(
                ticker=ticker, 
                quantity=quantity,
                average_buy_price=avg_price
            ))

    elif side == "sell":
        found = False
        for item in team.portfolio:
            if item.ticker == ticker:
                if item.quantity < quantity:
                    raise HTTPException(status_code=400, detail="Not enough shares!")
                
                item.quantity -= quantity
                if item.quantity == 0:
                    team.portfolio.remove(item)
                found = True
                break
        if not found:
             raise HTTPException(status_code=400, detail="You don't own this stock")
             
        team.cash_balance += total_cost

    await team.save()
    
    # --- SAVE HISTORY ---
    new_trade = Trade(
        team_id=team_id,
        ticker=ticker,
        side=side.upper(), 
        quantity=quantity,
        price=avg_price,   
        total=total_cost,
        dealer_id=dealer_id
    )
    await new_trade.insert()

    return {
        "status": "success",
        "ticker": ticker,
        "side": side,
        "execution_price_avg": round(avg_price, 2),
        "new_cash_balance": round(team.cash_balance, 2),
        "new_market_price": round(end_price, 2)
    }

@router.get("/teams/{team_id}/trades")
async def get_team_trades(team_id: str):
    trades = await Trade.find(Trade.team_id == team_id).sort(-Trade.timestamp).to_list()
    return trades