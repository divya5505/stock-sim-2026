from fastapi import APIRouter, HTTPException
from typing import List

# Import Models
from app.models.news import NewsFlash
from app.models.stock import Stock
from app.models.scenario import Scenario  # <--- Now we use the DB model

router = APIRouter()

# 1. PUBLIC: Get News Feed
@router.get("/")
async def get_news() -> List[NewsFlash]:
    # Returns the 10 most recent headlines, newest first
    return await NewsFlash.find_all().sort(-NewsFlash.created_at).limit(10).to_list()

# 2. DEALER: Execute a Pre-Made Scenario (From Database)
@router.post("/publish/{scenario_id}")
async def publish_scenario(scenario_id: str):
    # A. Look up the Script in MONGODB
    scenario = await Scenario.find_one(Scenario.scenario_id == scenario_id)
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario ID not found")
    
    # B. Publish News (Visual)
    # If sentiment is positive (>0), tag as POSITIVE (Green), else NEGATIVE (Red)
    visual_tag = "POSITIVE" if scenario.sentiment > 0 else "NEGATIVE"
    
    new_news = NewsFlash(
        headline=scenario.headline, 
        impact=visual_tag
    )
    await new_news.insert()

    # C. EXECUTE MARKET SHOCK (The Math)
    # We update the 'base_price' (S_t) directly.
    # New Price = Old Price * (1 + sentiment)
    
    stock = await Stock.find_one(Stock.ticker == scenario.ticker)
    
    new_price = 0.0 # Placeholder for return
    
    if stock:
        old_price = stock.base_price
        shock_factor = 1 + scenario.sentiment
        
        # Apply the Math
        stock.base_price = old_price * shock_factor
        await stock.save()
        
        # Force sync to ensure next trade sees new price immediately
        await stock.sync() 
        new_price = stock.base_price
        
        print(f"⚠ SHOCK APPLIED: {stock.ticker} moved from {old_price} to {stock.base_price}")
    
    return {
        "message": "Scenario Executed", 
        "headline": scenario.headline,
        "stock_impacted": scenario.ticker,
        "new_price_base": new_price
    }