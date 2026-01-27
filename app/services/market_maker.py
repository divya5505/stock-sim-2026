import asyncio
import random
import math
from app.models.stock import Stock
from beanie.operators import Set
from app.models.config import MarketStatus

VOLATILITY_MAP = {
    "BLUE": 0.005, 
    "VOLT": 0.015, 
    "TECH": 0.03, 
    "GOLD": 0.002, 
    "JUNK": 0.08 
}

async def update_prices():
    print("🚀 Market Maker Engine: STARTED")
    
    # Track state so we only print ONCE when status changes
    was_open = True 
    
    while True:
        # --- 1. SILENT CHECK ---
        if not MarketStatus.is_open:
            # If we just switched from Open -> Closed, print ONCE.
            if was_open:
                print("⏸ Market Maker Paused (Market Closed)")
                was_open = False
            
            # Sleep silently (No annoying print loop)
            await asyncio.sleep(5)
            continue
        
        # If we just switched from Closed -> Open, print ONCE.
        if not was_open:
            print("▶ Market Maker Resumed")
            was_open = True

        # --- 2. Normal Logic ---
        stocks = await Stock.find_all().to_list()
        
        if not stocks:
            # Keep this warning, it's actually important
            print("⚠ Market Maker: No stocks found. Waiting...")
            await asyncio.sleep(5)
            continue

        for stock in stocks:
            sigma = VOLATILITY_MAP.get(stock.ticker, 0.01)
            shock = random.gauss(0, sigma)
            
            price_t_minus_1 = stock.current_price 
            new_price = price_t_minus_1 * math.exp(shock)
            
            if new_price < 5.0:
                new_price = 5.0

            await stock.update(Set({
                Stock.current_price: new_price,
                Stock.previous_price: price_t_minus_1
            }))

        await asyncio.sleep(5)

async def start_market_maker():
    asyncio.create_task(update_prices())