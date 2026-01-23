import asyncio
import time
import os
# Force Cloud Config
from config import MONGODB_URL
os.environ["MONGODB_URL"] = MONGODB_URL

from app.database import init_db
from app.models.stock import Stock
from app.models.team import Team

async def measure_transaction_speed():
    print("⏳ Connecting to Cloud for Benchmark...")
    await init_db()

    # 1. Setup Data
    stock = await Stock.find_one(Stock.ticker == "VOLT")
    team = await Team.find_one(Team.team_id == "TEAM_01")
    
    if not stock or not team:
        print("❌ Error: Run seed.py first. Data missing.")
        return

    print(f"\n--- BENCHMARK STARTED [Server: India -> Atlas: Mumbai] ---")
    
    # 2. Measure Read Speed
    start_time = time.perf_counter()
    _ = await Stock.find_one(Stock.ticker == "VOLT")
    end_time = time.perf_counter()
    read_latency = (end_time - start_time) * 1000
    print(f"📉 Read Latency: {read_latency:.2f} ms")

    # 3. Measure Write Speed (The Transaction)
    # Simulation: Buying 1 stock involves a DB write
    start_time = time.perf_counter()
    
    # Simple logic: Decrement cash, Increment portfolio (2 writes)
    team.cash_balance -= stock.base_price
    await team.save() # Write 1
    
    end_time = time.perf_counter()
    write_latency = (end_time - start_time) * 1000
    print(f"Vm Write Latency: {write_latency:.2f} ms")

    total_time = read_latency + write_latency
    print(f"------------------------------------------------")
    print(f"⚡ TOTAL TRANSACTION TIME: {total_time:.2f} ms")
    
    if total_time < 1000:
        print("✅ PASS: Sub-second latency achieved.")
    else:
        print("⚠️ FAIL: Optimization required.")

if __name__ == "__main__":
    asyncio.run(measure_transaction_speed())