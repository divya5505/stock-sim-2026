import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Your Cloud URL
ATLAS_URL = "mongodb+srv://Divya:Dayal2005@cluster0.e2ibnmi.mongodb.net/stock_market_simulator?appName=Cluster0&retryWrites=true&w=majority"

async def reset_teams():
    print("🔄 CONNECTING TO DATABASE...")
    client = AsyncIOMotorClient(ATLAS_URL)
    db = client.stock_market_simulator
    teams_collection = db.teams
    
    print("🧹 RESETTING ALL TEAMS...")
    
    # Update ALL documents in the 'teams' collection
    result = await teams_collection.update_many(
        {}, # Empty filter selects everyone
        {
            "$set": {
                "cash_balance": 10000.0,  # Reset cash
                "portfolio": []            # Empty the portfolio list
            }
        }
    )
    
    print(f"✅ RESET COMPLETE.")
    print(f"   - Updates applied to {result.matched_count} teams.")
    print("   - All Cash Balances set to $100,000")
    print("   - All Portfolios wiped clean.")

if __name__ == "__main__":
    asyncio.run(reset_teams())