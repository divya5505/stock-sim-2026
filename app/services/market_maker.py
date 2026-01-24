import asyncio
import random
import math
from app.models.stock import Stock
from beanie.operators import Set # <--- ADD THIS IMPORT

VOLATILITY_MAP = {
    "BLUE": 0.005, 
    "VOLT": 0.015, 
    "TECH": 0.03, 
    "GOLD": 0.002, 
    "JUNK": 0.08 
}

async def update_prices():
    print("🚀 Market Maker Engine: STARTED")
    while True:
        stocks = await Stock.find_all().to_list()
        
        if not stocks:
            print("⚠ Market Maker: No stocks found. Waiting...")
            await asyncio.sleep(5)
            continue

        for stock in stocks:
            sigma = VOLATILITY_MAP.get(stock.ticker, 0.01)
            shock = random.gauss(0, sigma)
            
            # 1. Calculate the New Price based on the Drift
            # We use the current base_price as the starting point
            new_price = stock.base_price * math.exp(shock)
            
            # 2. Safety Floor
            if new_price < 5.0:
                new_price = 5.0

            # 3. ATOMIC UPDATE (The Fix)
            # Instead of stock.save(), we tell MongoDB: "Set the price to X"
            # This prevents it from accidentally overwriting a News Event.
            await stock.update(Set({Stock.base_price: new_price}))

        await asyncio.sleep(5)

async def start_market_maker():
    asyncio.create_task(update_prices())