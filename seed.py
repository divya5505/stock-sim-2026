import asyncio
from app.database import init_db
from app.models.dealer import Dealer
from app.models.stock import Stock
from app.models.team import Team
from app.models.scenario import Scenario  # <--- Added Import

# --- CONFIGURATION ---

# 1. STOCK DATA
STOCKS = [
    {"ticker": "BLUE", "name": "Blue Chip Ind", "price": 500.0},
    {"ticker": "VOLT", "name": "Volt Energy", "price": 150.0},
    {"ticker": "TECH", "name": "Tech StartUp", "price": 80.0},
    {"ticker": "GOLD", "name": "Gold Reserves", "price": 2000.0},
    {"ticker": "JUNK", "name": "Meme Holdings", "price": 20.0},
]

# 2. SCENARIO DATA (The "Weapons" for the Event)
SCENARIOS_DATA = [
    {"id": "WAR_01", "headline": "BREAKING: Conflict Erupts in Oil Region!", "ticker": "VOLT", "sentiment": 0.25},
    {"id": "SCANDAL_01", "headline": "FRAUD ALERT: Tech Startup CEO arrested.", "ticker": "TECH", "sentiment": -0.30},
    {"id": "REGULATION_01", "headline": "GOVT BAN: New regulations on sugary drinks.", "ticker": "BLUE", "sentiment": -0.10},
    {"id": "DISCOVERY_01", "headline": "GOLD RUSH: Massive new deposit found.", "ticker": "GOLD", "sentiment": -0.15},
    {"id": "MEME_PUMP", "headline": "Reddit army targets Junk Holdings. 🚀", "ticker": "JUNK", "sentiment": 0.50}
]

async def seed_data():
    print("⏳ Connecting to Database...")
    await init_db()
    
    # 1. CLEAR OLD DATA (Wipe everything for a clean start)
    print("🧹 Wiping old 'Zombie' data...")
    await Dealer.delete_all()
    await Stock.delete_all()
    await Team.delete_all()
    await Scenario.delete_all() # <--- Wipes old scenarios too
    
    credentials_log = []
    credentials_log.append("=== STOCK MARKET SIMULATOR 2.0 CREDENTIALS ===\n")

    # 2. CREATE DEALERS
    print("Creating Dealers...")
    credentials_log.append("\n--- DEALER LOGINS (Give to Volunteers) ---")
    for i in range(1, 6):
        username = f"DEALER_{i}"
        password = f"admin{i}23" 
        await Dealer(username=username, password=password).insert()
        credentials_log.append(f"User: {username} | Pass: {password}")

    # 3. CREATE STOCKS
    print("Creating Stocks...")
    for s in STOCKS:
        await Stock(
            ticker=s["ticker"], 
            company_name=s["name"], 
            base_price=s["price"], 
            dealer_inventory=0
        ).insert()

    # 4. CREATE SCENARIOS
    print("Loading Scenarios...")
    for s in SCENARIOS_DATA:
        await Scenario(
            scenario_id=s["id"],
            headline=s["headline"],
            ticker=s["ticker"],
            sentiment=s["sentiment"]
        ).insert()

    # 5. CREATE TEAMS
    print("Creating Teams...")
    credentials_log.append("\n--- TEAM LOGINS (Give to Students) ---")
    for i in range(1, 16):
        team_id = f"TEAM_{i:02d}" # TEAM_01, TEAM_02...
        name = f"Squad {i}"
        password = f"trade{i}{i}!" 
        
        await Team(
            team_id=team_id, 
            name=name, 
            password=password, 
            cash_balance=100000.0,
            portfolio=[]
        ).insert()
        credentials_log.append(f"Team: {team_id} | Pass: {password}")

    # 6. SAVE CREDENTIALS TO FILE
    with open("secret_credentials.txt", "w") as f:
        f.write("\n".join(credentials_log))
    
    print("✅ SUCCESS! System Reset.")
    print("📄 Check 'secret_credentials.txt' for your passwords.")

if __name__ == "__main__":
    asyncio.run(seed_data())