import time
import asyncio
from snap_core import load_settings, fetch_current_price, apply_status

while True:
    try:
        settings = load_settings()
        result = fetch_current_price(settings)
        asyncio.run(apply_status(result["current_energy"], result["today_prices"], settings))
        time.sleep(60)
    except Exception as e:
        print("Error in runner:", e)
        time.sleep(10)
