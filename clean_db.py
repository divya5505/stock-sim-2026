import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# SAME URL AS DATABASE.PY
ATLAS_URL = "mongodb+srv://Divya:Dayal2005@cluster0.e2ibnmi.mongodb.net/stock_market_simulator?appName=Cluster0&retryWrites=true&w=majority"

async def nuke():
    print("🚀 CONNECTING TO CLOUD...")
    client = AsyncIOMotorClient(ATLAS_URL)
    db = client.stock_market_simulator
    
    # 1. Check Count Before
    count_before = await db.teams.count_documents({})
    print(f"🧐 FOUND {count_before} TEAMS.")

    # 2. DELETE EVERYTHING
    await db.teams.delete_many({})
    print("💥 DELETED ALL TEAMS.")

    # 3. Verify
    count_after = await db.teams.count_documents({})
    print(f"✅ TEAMS REMAINING: {count_after}")
    print("The database is now EMPTY. You can register fresh.")

if __name__ == "__main__":
    asyncio.run(nuke())