from fastapi import APIRouter, HTTPException, Body
from app.models.stock import Stock
from app.models.team import Team, PortfolioItem
from app.models.dealer import Dealer

router = APIRouter()

# --- CONFIGURATION ---
MAX_SHARES_PER_TEAM = 1000 # Hard Regulatory Limit (Anti-Monopoly)
MIN_PRICE_FLOOR = 5.0      # Circuit Breaker Floor (Anti-Crash)

# --- 1. GET PRICES ---
@router.get("/prices")
async def get_prices():
    stocks = await Stock.find_all().to_list()
    return [{
        "ticker": s.ticker,
        "price": round(s.current_price, 2),
        "trend": "UP" if s.dealer_inventory < 0 else "DOWN" 
    } for s in stocks]

# --- 2. EXECUTE TRADE (With Security Checks) ---
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
    
    # Check 1: The "Suicide Bomber" Fix (Price Floor)
    if side == "sell" and stock.current_price <= MIN_PRICE_FLOOR:
        raise HTTPException(status_code=400, detail="Market Halted: Price too low to sell!")

    # Check 2: The "Monopoly" Fix (Absolute Cap)
    if side == "buy":
        current_holding = 0
        for item in team.portfolio:
            if item.ticker == ticker:
                current_holding = item.quantity
                break
        
        # If buying exceeds 1000 shares total -> REJECT
        if (current_holding + quantity) > MAX_SHARES_PER_TEAM:
             raise HTTPException(
                 status_code=400, 
                 detail=f"REGULATORY LIMIT: You cannot hold more than {MAX_SHARES_PER_TEAM} shares of {ticker}!"
             )
    # -----------------------

    # B. CALCULATE SLIPPAGE
    start_inventory = stock.dealer_inventory
    start_price = stock.base_price - (stock.sensitivity * start_inventory)
    # Ensure floor applies to math
    start_price = max(MIN_PRICE_FLOOR, start_price)
    
    if side == "buy":
        end_inventory = start_inventory - quantity
    else:
        end_inventory = start_inventory + quantity
        
    end_price = stock.base_price - (stock.sensitivity * end_inventory)
    end_price = max(MIN_PRICE_FLOOR, end_price)
    
    avg_price = (start_price + end_price) / 2
    total_cost = avg_price * quantity

    # C. EXECUTE TRANSACTION
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
            
        stock.dealer_inventory = end_inventory 

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
        stock.dealer_inventory = end_inventory

    await team.save()
    await stock.save()

    return {
        "status": "success",
        "ticker": ticker,
        "side": side,
        "execution_price_avg": round(avg_price, 2),
        "new_cash_balance": round(team.cash_balance, 2)
    }