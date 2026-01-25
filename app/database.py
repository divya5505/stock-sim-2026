import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# --- IMPORT MODELS ---
from app.models.stock import Stock
from app.models.team import Team
from app.models.dealer import Dealer
from app.models.scenario import Scenario
from app.models.news import NewsFlash 

# --- THE HARDCODED CLOUD URL ---
# This guarantees the app CANNOT connect to localhost.
# ATLAS_URL = "mongodb+srv://Divya:Dayal2005@cluster0.e2ibnmi.mongodb.net/stock_market_simulator?appName=Cluster0&retryWrites=true&w=majority"
ATLAS_URL = os.environ["MONGODB_URL"]

async def init_db():
    print(f"\n🔌 ATTEMPTING CONNECTION TO CLOUD...")
    print(f"🌍 Target URL: {ATLAS_URL[:40]}...")

    # 1. Direct Connection (No os.getenv, no localhost fallback)
    client = AsyncIOMotorClient(ATLAS_URL)
    
    # 2. Select Database
    database = client.stock_market_simulator

    # 3. Initialize
    await init_beanie(
        database=database, 
        document_models=[Stock, Team, Dealer, Scenario, NewsFlash]
    )
    print("✅ SUCCESS! Connected to MongoDB Atlas (Cloud). Localhost is ignored.\n")