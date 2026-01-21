from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.stock import Stock
from app.models.team import Team
from app.models.dealer import Dealer
from app.models.scenario import Scenario
from app.models.news import NewsFlash # <--- Ensure this is here

# You can use your existing MongoDB Atlas URL here
MONGO_URL = "mongodb://localhost:27017" # Or your Atlas connection string

async def init_db():
    # 1. Create the client (The connection)
    client = AsyncIOMotorClient(MONGO_URL)
    
    # 2. Select the database
    database = client.stock_market_simulator  # Name of your DB
    
    # 3. Initialize Beanie (The Mongoose equivalent)
    # This automatically links your Models to the DB
    await init_beanie(database=database, document_models=[Stock,Team,Dealer,Scenario,NewsFlash])