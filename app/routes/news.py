import datetime
from fastapi import APIRouter, HTTPException, Body
from typing import List
from pydantic import BaseModel
from beanie.operators import Set  

# Import Models
from app.models.news import NewsFlash
from app.models.stock import Stock
from app.models.scenario import Scenario 

router = APIRouter()

# --- INPUT MODELS ---
class NewsCreateRequest(BaseModel):
    scenario_id: str
    headline: str
    ticker: str
    sentiment: float 

# # 1. PUBLIC: Get News Feed
# @router.get("/")
# async def get_news() -> List[NewsFlash]:
#     return await NewsFlash.find_all().sort(-NewsFlash.created_at).limit(10).to_list()

# 2. DEALER: Execute a Pre-Made Scenario
@router.post("/publish/{scenario_id}")
async def publish_scenario(scenario_id: str):
    # A. Look up the Script
    scenario = await Scenario.find_one(Scenario.scenario_id == scenario_id)
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario ID not found")
    
    # B. Publish News (Visual)
    visual_tag = "POSITIVE" if scenario.sentiment > 0 else "NEGATIVE"
    if scenario.sentiment == 0: visual_tag = "INFO"
    
    new_news = NewsFlash(
        headline=scenario.headline, 
        impact=visual_tag,
        ticker=scenario.ticker,
        sentiment=scenario.sentiment
    )
    await new_news.insert()

    # C. EXECUTE MARKET SHOCK
    await apply_market_shock(scenario.ticker, scenario.sentiment)
    
    return {"message": "Scenario Published", "headline": scenario.headline}

# 3. CREATE ROUTE (FIXED: NOW UPDATES PRICE)
@router.post("/")
async def create_news_scenario(data: NewsCreateRequest):
    print(f"📰 [DEBUG] New Scenario Request: {data.headline}")

    # A. Determine Visual Tag
    impact_str = "INFO"
    if data.sentiment > 0:
        impact_str = "POSITIVE"
    elif data.sentiment < 0:
        impact_str = "NEGATIVE"

    # B. Save to Database FIRST
    new_flash = NewsFlash(
        headline=data.headline,
        impact=impact_str,
        ticker=data.ticker,
        scenario_id=data.scenario_id,
        sentiment=data.sentiment
    )
    await new_flash.save()
    print(f"✅ [DEBUG] Saved News to DB: {new_flash.id}")

    # C. EXECUTE MARKET SHOCK (Using the data we just saved)
    # This ensures the math happens AFTER storage, as you requested.
    new_price = await apply_market_shock(new_flash.ticker, new_flash.sentiment)

    return {
        "message": "Scenario created and executed", 
        "id": str(new_flash.id),
        "new_price": new_price
    }

# --- HELPER FUNCTION ---
# I moved the math here so you don't have to write it twice!
async def apply_market_shock(ticker_str: str, sentiment: float):
    # 1. Clean Ticker
    clean_ticker = ticker_str.strip().upper()
    stock = await Stock.find_one(Stock.ticker == clean_ticker)
    
    if not stock:
        print(f"❌ WARNING: News created for unknown stock: {clean_ticker}")
        return 0.0

    # 2. Calculate New Price
    old_price = stock.base_price
    shock_multiplier = 1 + sentiment
    new_base_price = old_price * shock_multiplier

    # 3. Apply Atomic Update
    await stock.update(Set({Stock.base_price: new_base_price}))
    
    print(f"⚠ SHOCK APPLIED: {clean_ticker}")
    print(f"   📉 Old: {round(old_price, 2)} -> 📈 New: {round(new_base_price, 2)}")
    
    return new_base_price