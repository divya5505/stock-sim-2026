from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List

# --- IMPORTS ---
from app.models.stock import Stock
from app.models.team import Team, PortfolioItem
from app.models.dealer import Dealer

from beanie.operators import Set

router = APIRouter()

# --- CONFIGURATION ---
MAX_SHARES_PER_TEAM = 10000
MIN_PRICE_FLOOR = 5.0      

# --- NEW: DEALER LOGIN MODEL ---
class DealerLoginRequest(BaseModel):
    username: str
    password: str

# --- 1. DEALER LOGIN (Fixes the 404 Error) ---
@router.post("/dealer/login")
async def dealer_login(data: DealerLoginRequest):
    # 1. Find Dealer
    dealer = await Dealer.find_one(Dealer.username == data.username)
    
    # 2. Validate Credentials
    if not dealer:
        raise HTTPException(status_code=401, detail="Invalid username")
        
    if dealer.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid password")

    # 3. Success
    return {
        "message": "Login successful", 
        "username": dealer.username,
        "role": "dealer"
    }

# --- 2. GET PRICES ---
@router.get("/prices")
async def get_prices():
    stocks = await Stock.find_all().to_list()
    
    response_data = []
    
    for s in stocks:
        # Trend is based on price movement relative to the day's start
        trend_direction = "UP" if s.current_price >= s.base_price else "DOWN"
        display_name = getattr(s, 'name', s.ticker) 

        response_data.append({
            "ticker": s.ticker,
            "company_name": display_name,
            "current_price": round(s.current_price, 2),
            "base_price": round(s.base_price, 2), 
            "trend": trend_direction
        })
        
    return response_data

# --- 3. EXECUTE TRADE (FIXED LOGIC) ---
@router.post("/trade")
async def trade_stock(
    team_id: str = Body(),
    ticker: str = Body(),
    quantity: int = Body(),
    side: str = Body(), 
    dealer_id: str = Body(),
    dealer_password: str = Body()
):
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

    # --- SECURITY CHECKS ---
    if side == "sell" and stock.current_price <= MIN_PRICE_FLOOR:
        raise HTTPException(status_code=400, detail="Market Halted: Price too low to sell!")

    if side == "buy":
        current_holding = 0
        for item in team.portfolio:
            if item.ticker == ticker:
                current_holding = item.quantity
                break
        
        if (current_holding + quantity) > MAX_SHARES_PER_TEAM:
             raise HTTPException(
                 status_code=400, 
                 detail=f"REGULATORY LIMIT: You cannot hold more than {MAX_SHARES_PER_TEAM} shares of {ticker}!"
             )

    # --- B. CALCULATE SLIPPAGE (CORRECTED) ---
    # 1. Start from the CURRENT market price (includes Random Walk history)
    start_price = stock.base_price
    
    
    # 2. Calculate impact (Sensitivity * Quantity)
    # Higher sensitivity = Price moves more per share traded
    impact = stock.sensitivity * quantity
    
    if side == "buy":
        # Buying pushes price UP
        end_price = start_price + impact
        # Dealer sells to you, inventory drops
        end_inventory = stock.dealer_inventory - quantity
    else: 
        # Selling pushes price DOWN
        end_price = start_price - impact
        # Dealer buys from you, inventory rises
        end_inventory = stock.dealer_inventory + quantity
        
    # 3. Apply Safety Floors
    start_price = max(MIN_PRICE_FLOOR, start_price)
    end_price = max(MIN_PRICE_FLOOR, end_price)
    
    # 4. Calculate Average Execution Price
    avg_price = (start_price + end_price) / 2
    total_cost = avg_price * quantity
    
    # IMPORTANT: Update the stock's state!
    await stock.update(Set({Stock.base_price: end_price}))
    await stock.update(Set({Stock.dealer_inventory: end_inventory}))



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

    # Save changes to DB
    await team.save()
    await stock.save()

    return {
        "status": "success",
        "ticker": ticker,
        "side": side,
        "execution_price_avg": round(avg_price, 2),
        "new_cash_balance": round(team.cash_balance, 2),
        "new_market_price": round(end_price, 2)
    }