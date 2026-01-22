from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- NEW IMPORT
from app.database import init_db
from app.routes import market, teams, news
from app.services.market_maker import start_market_maker

app = FastAPI()

# --- CORS CONFIGURATION (The React Connection) ---
# This allows the React app (running on a different URL) to talk to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any website to connect (safest for the event)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
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

# Register all routes
app.include_router(market.router, prefix="/api", tags=["Market"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(news.router, prefix="/api/news", tags=["News"])

@app.get("/")
async def root():
    return {"message": "Stock Market Simulator 2.0 is Live"}