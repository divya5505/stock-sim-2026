import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# --- IMPORT MODELS ---
from app.models.stock import Stock
from app.models.team import Team
from app.models.dealer import Dealer
from app.models.scenario import Scenario
from app.models.news import NewsFlash
from app.models.trade import Trade  # <--- FIXED IMPORT (was app.routes.trade)

# ATLAS_URL = "mongodb+srv://Divya:Dayal2005@cluster0.e2ibnmi.mongodb.net/stock_market_simulator?appName=Cluster0&retryWrites=true&w=majority"
ATLAS_URL = os.environ["MONGODB_URL"]

async def init_db():
    print(f"\n🔌 ATTEMPTING CONNECTION TO CLOUD...")
    # client = AsyncIOMotorClient(ATLAS_URL)
    client = AsyncIOMotorClient(ATLAS_URL, uuidRepresentation="standard") # Added uuidRep just in case
    
    database = client.stock_market_simulator

    await init_beanie(
        database=database, 
        document_models=[Stock, Team, Dealer, Scenario, NewsFlash, Trade]
    )
    print("✅ SUCCESS! Connected to MongoDB Atlas (Cloud).\n")