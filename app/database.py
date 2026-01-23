import os  # <--- Required to read the environment variable
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.stock import Stock
from app.models.team import Team
from app.models.dealer import Dealer
from app.models.scenario import Scenario
from app.models.news import NewsFlash 

async def init_db():
    # 1. GET THE URL
    # Priority: Check if 'seed.py' or DigitalOcean provided a specific link.
    # If not found, default to localhost.
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

    # 2. Create the client
    client = AsyncIOMotorClient(mongo_url)
    
    # 3. Select the database
    # Note: If the URL includes the db name (like in config.py), motor handles it. 
    # But we explicitly select it here to be safe.
    database = client.stock_market_simulator

    # 4. Initialize Beanie
    await init_beanie(
        database=database, 
        document_models=[Stock, Team, Dealer, Scenario, NewsFlash]
    )