from fastapi import FastAPI
from app.database import init_db
from app.routes import market, teams, news  # <--- 1. Import 'news'
from app.services.market_maker import start_market_maker # <--- 2. Import the Background Service

app = FastAPI()

@app.on_event("startup")
async def start_system():
    # A. Connect to Database
    await init_db()
    print("✅ Database Connected!")
    
    # B. Start the Background Simulation (The Drift)
    # This makes the market "alive" even when no one is trading
    await start_market_maker() 

# Register all routes
app.include_router(market.router, prefix="/api", tags=["Market"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(news.router, prefix="/api/news", tags=["News"]) # <--- 3. Register News

@app.get("/")
async def root():
    return {"message": "Stock Market Simulator 2.0 is Live"}