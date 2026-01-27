import asyncio
import random
import math
from app.models.stock import Stock
from beanie.operators import Set 

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
            # 1. Get Volatility
            sigma = VOLATILITY_MAP.get(stock.ticker, 0.01)
            shock = random.gauss(0, sigma)
            
            # 2. CAPTURE HISTORY (Crucial for the Arrow)
            # We save the price BEFORE the shock as 'previous_price'
            price_t_minus_1 = stock.current_price 

            # 3. CALCULATE NEW PRICE (The Fix)
            # We apply the shock to the CURRENT price, not the base price.
            # This ensures we don't erase the impact of recent trades or news.
            new_price = price_t_minus_1 * math.exp(shock)
            
            # 4. Safety Floor
            if new_price < 5.0:
                new_price = 5.0

            # 5. ATOMIC UPDATE
            # - We update 'current_price' to the new value.
            # - We update 'previous_price' to the old value (so the arrow works).
            # - We DO NOT touch 'base_price' (that stays as the day's Open Price).
            await stock.update(Set({
                Stock.current_price: new_price,
                Stock.previous_price: price_t_minus_1
            }))

        await asyncio.sleep(5)

async def start_market_maker():
    asyncio.create_task(update_prices())