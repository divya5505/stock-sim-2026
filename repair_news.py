import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Your Cloud URL
ATLAS_URL = "mongodb+srv://Divya:Dayal2005@cluster0.e2ibnmi.mongodb.net/stock_market_simulator?appName=Cluster0&retryWrites=true&w=majority"

async def fix_market():
    print("🔧 CONNECTING TO DATABASE...")
    client = AsyncIOMotorClient(ATLAS_URL)
    db = client.stock_market_simulator
    stocks = db.stocks
    
    print("🧹 RESETTING INVENTORIES...")
    
    # 1. Reset Dealer Inventory to 0 for ALL stocks
    # This removes the massive "sell pressure" dragging the price down.
    await stocks.update_many(
        {}, 
        {"$set": {"dealer_inventory": 0}}
    )
    
    # 2. Reset Base Prices to a healthy starting point (Optional)
    # This ensures they start at a visible, movable price (e.g., 100.00)
    await stocks.update_many(
        {}, 
        {"$set": {"base_price": 100.00}}
    )

    print("✅ MARKET NORMALIZED.")
    print("   - All Inventories set to 0")
    print("   - All Base Prices set to 100.00")
    print("🚀 Restart your server and watch the prices move!")

if __name__ == "__main__":
    asyncio.run(fix_market())