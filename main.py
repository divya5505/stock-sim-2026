from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- NEW IMPORT
from app.database import init_db
from app.routes import market, teams, news
from app.services.market_maker import start_market_maker

app = FastAPI()

origins = [
    "http://localhost:5500",      # VS Code Live Server
    "http://127.0.0.1:5500",      # VS Code Live Server (IP version)
    "http://localhost:8000",      # Your Backend (Self-communication)
]

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],  
    allow_headers=["*"],
)
@app.on_event("startup")
async def start_system():
    # A. Connect to Database
    await init_db()
    print("✅ Database Connected!")
    
    # B. Start the Background Simulation (The Drift)
    # This makes the market "alive" even when no one is trading
    await start_market_maker() 

# 1. The Correct "Canonical" Routes (As per your documentation)
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(market.router, prefix="/api/stocks", tags=["Stocks"]) # or /api/prices if you prefer
# app.include_router(dealer.router, prefix="/api/dealer", tags=["Dealer"])
app.include_router(news.router, prefix="/api/news", tags=["News"])

# 2. The "Compatibility Layer" (Fixing the Frontend Mismatch)
# The frontend is asking for /api/v1/stocks/prices. 
# By mounting the SAME router to this prefix, we redirect their requests to the right logic.
app.include_router(market.router, prefix="/api/v1/stocks", tags=["Stocks (Legacy Support)"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams (Legacy)"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News (Legacy)"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Market (Trade)"])

@app.get("/")
async def root():
    return {"message": "Stock Market Simulator 2.0 is Live"}