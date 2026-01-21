import asyncio
import random
import math
from app.models.stock import Stock

# Volatility Settings (Standard Deviation)
# Higher number = More crazy movement
VOLATILITY_MAP = {
    "BLUE": 0.005,  # 0.5% swings (Safe)
    "VOLT": 0.015,  # 1.5% swings (Standard)
    "TECH": 0.03,   # 3.0% swings (High Risk)
    "GOLD": 0.002,  # 0.2% swings (Stable)
    "JUNK": 0.08    # 8.0% swings (Chaos)
}

async def update_prices():
    """
    The Heartbeat of the Market.
    Runs every 5 seconds to apply Natural Drift.
    Formula: S_new = S_old * e^(random_shock)
    """
    while True:
        stocks = await Stock.find_all().to_list()
        
        if not stocks:
            print("⚠ Market Maker: No stocks found. Waiting...")
            await asyncio.sleep(5)
            continue

        print(f"📉 Market Maker: Updating {len(stocks)} stocks...")

        for stock in stocks:
            # 1. Get Volatility (Default to 1% if unknown)
            sigma = VOLATILITY_MAP.get(stock.ticker, 0.01)
            
            # 2. Generate Random Shock (Normal Distribution)
            # Mean=0, StdDev=sigma
            shock = random.gauss(0, sigma)
            
            # 3. Apply the Formula: S_new = S_old * e^(shock)
            # We update the 'base_price' because the final price 
            # is calculated dynamically as (base_price - dealer_impact)
            stock.base_price = stock.base_price * math.exp(shock)
            
            # 4. Save to DB
            await stock.save()

        # Sleep for 5 seconds before next update
        await asyncio.sleep(5)

async def start_market_maker():
    print("🚀 Market Maker Engine: STARTED")
    asyncio.create_task(update_prices())