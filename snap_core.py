import json
import socket
import requests
import RPi.GPIO as GPIO
from pywizlight import wizlight, PilotBuilder
import asyncio

SETTINGS_FILE = "snap-settings.json"

# --- Load settings ---
def load_settings():
    with open(SETTINGS_FILE) as f:
        return json.load(f)

# --- Resolve Wiz IP ---
def resolve_ip(hostname, fallback):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return fallback

# --- GPIO LED Control ---
def snap_led(pin, state, enabled=True):
    if not enabled:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH if state == "on" else GPIO.LOW)

# --- Fetch Tibber energy price ---
def fetch_current_price(settings):
    endpoint = 'https://api.tibber.com/v1-beta/gql'
    headers = {
        'Authorization': f"Bearer {settings['tibber_api_key']}",
        'Content-Type': 'application/json'
    }

    query = """{
    viewer {
        homes {
        currentSubscription {
            priceInfo {
            current {
                total
                energy
                tax
                startsAt
            }
            today {
                total
                energy
                tax
                startsAt
            }
            }
        }
        }
    }
    }"""


    response = requests.post(endpoint, json={'query': query}, headers=headers)
    data = response.json()['data']['viewer']['homes'][settings['home_index']]['currentSubscription']['priceInfo']
    return {
        "current_energy": data['current']['total'],
        "today_prices": data['today']
    }

# --- Determine status from price ---
def classify_price_status(current_energy, breakpoints):
    if current_energy > breakpoints["very_expensive"]:
        return "very_expensive"
    elif current_energy > breakpoints["expensive"]:
        return "expensive"
    elif current_energy > breakpoints["ok"]:
        return "ok"
    elif current_energy > breakpoints["cheap"]:
        return "cheap"
    else:
        return "very_cheap"

# --- Return UI-ready status ---
def get_status():
    try:
        settings = load_settings()
        result = fetch_current_price(settings)
        status = classify_price_status(result["current_energy"], settings["price_breakpoints"])

        # NEW: average energy price and status
        today_prices = result["today_prices"]
        avg = sum(h['energy'] for h in today_prices) / 24
        avg_part = 0.6666667
        bp = settings["price_breakpoints"]

        if avg > (bp["very_expensive"] * avg_part):
            avg_status = "very_expensive"
        elif avg > (bp["expensive"] * avg_part):
            avg_status = "expensive"
        elif avg > (bp["ok"] * avg_part):
            avg_status = "ok"
        elif avg > (bp["cheap"] * avg_part):
            avg_status = "cheap"
        else:
            avg_status = "very_cheap"

        return {
            "current_energy": f"{result['current_energy']:.2f}".replace(".", ","),
            "status": status,
            "average_energy": avg,
            "average_status": avg_status,
            "raw_hours": [
                {
                    "startsAt": hour["startsAt"],
                    "total": hour["total"]
                }
                for hour in today_prices
                if "startsAt" in hour and "total" in hour
            ]

        }


    except Exception as e:
        return {"error": str(e)}

# --- Apply status to LEDs and Wiz light ---
async def apply_status(current_energy, today_prices, settings):
    wiz_enabled = settings.get("wiz", False)
    led_enabled = settings.get("led", False)
    breakpoints = settings["price_breakpoints"]
    status = classify_price_status(current_energy, breakpoints)
    ip = resolve_ip(settings["wiz_hostname"], settings["wiz_fallback_ip"])
    light = wizlight(ip) if wiz_enabled else None

    # GPIO logic
    if status == "very_expensive":
        snap_led(18, "on", led_enabled)
        snap_led(23, "off", led_enabled)
        snap_led(24, "off", led_enabled)
        if light: await light.turn_on(PilotBuilder(rgb=(255, 0, 0)))
    elif status == "expensive":
        snap_led(18, "on", led_enabled)
        snap_led(23, "on", led_enabled)
        snap_led(24, "off", led_enabled)
        if light: await light.turn_on(PilotBuilder(rgb=(255, 50, 0)))
    elif status == "ok":
        snap_led(18, "off", led_enabled)
        snap_led(23, "on", led_enabled)
        snap_led(24, "off", led_enabled)
        if light: await light.turn_on(PilotBuilder(rgb=(255, 140, 0)))
    elif status == "cheap":
        snap_led(18, "off", led_enabled)
        snap_led(23, "on", led_enabled)
        snap_led(24, "on", led_enabled)
        if light: await light.turn_on(PilotBuilder(rgb=(255, 255, 224)))
    else:
        snap_led(18, "off", led_enabled)
        snap_led(23, "off", led_enabled)
        snap_led(24, "on", led_enabled)
        if light: await light.turn_on(PilotBuilder(rgb=(255, 255, 255)))

    # Average logic (shortened)
    avg = sum(h['energy'] for h in today_prices) / 24
    av = 0.6666667
    if avg > (breakpoints["very_expensive"] * av):
        snap_led(25, "on", led_enabled)
        snap_led(8, "off", led_enabled)
        snap_led(7, "off", led_enabled)
    elif avg > (breakpoints["expensive"] * av):
        snap_led(25, "on", led_enabled)
        snap_led(8, "on", led_enabled)
        snap_led(7, "off", led_enabled)
    elif avg > (breakpoints["ok"] * av):
        snap_led(25, "off", led_enabled)
        snap_led(8, "on", led_enabled)
        snap_led(7, "off", led_enabled)
    elif avg > (breakpoints["cheap"] * av):
        snap_led(25, "off", led_enabled)
        snap_led(8, "on", led_enabled)
        snap_led(7, "on", led_enabled)
    else:
        snap_led(25, "off", led_enabled)
        snap_led(8, "off", led_enabled)
        snap_led(7, "on", led_enabled)

    # Blue "heartbeat" blink
    snap_led(16, "on", led_enabled)
    await asyncio.sleep(0.1)
    snap_led(16, "off", led_enabled)
