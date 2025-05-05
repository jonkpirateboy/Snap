import RPi.GPIO as GPIO
import asyncio
import requests
import time
import json
import socket

from pywizlight import wizlight, PilotBuilder

# Load settings
with open("snap-settings.json") as f:
    settings = json.load(f)

tibber_api_key = settings["tibber_api_key"]
wiz_hostname = settings["wiz_hostname"]
wiz_fallback_ip = settings["wiz_fallback_ip"]
home_index = settings["home_index"]
price_breakpoints = settings["price_breakpoints"]

very_expensive = price_breakpoints["very_expensive"]
expensive = price_breakpoints["expensive"]
ok = price_breakpoints["ok"]
cheap = price_breakpoints["cheap"]

# Resolve Wiz IP
try:
    ip = socket.gethostbyname(wiz_hostname)
except socket.gaierror:
    print(f"Could not resolve hostname '{wiz_hostname}'. Falling back to IP: {wiz_fallback_ip}")
    ip = wiz_fallback_ip

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = settings["led"]
wiz = settings["wiz"]

def snap_led(pin, state):
    if led:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH if state == 'on' else GPIO.LOW)

def snap_intro():
    for p in [18, 23, 24, 25, 8, 7, 16]:
        snap_led(p, "off")
    time.sleep(1)
    for p in [18, 23, 24, 25, 8, 7, 16]:
        snap_led(p, "on")
        time.sleep(0.5)
        snap_led(p, "off")

async def snap_check_current_energy_price():
    light = wizlight(ip) if wiz else None
    if current_energy > very_expensive:
        print('Live in cave now')
        snap_led(18, 'on'); snap_led(23, 'off'); snap_led(24, 'off')
        if wiz: await light.turn_on(PilotBuilder(rgb=(255, 0, 0)))
    elif current_energy > expensive:
        print('You can use one thing now')
        snap_led(18, 'on'); snap_led(23, 'on'); snap_led(24, 'off')
        if wiz: await light.turn_on(PilotBuilder(rgb=(255, 50, 0)))
    elif current_energy > ok:
        print('Turn on some stuff now')
        snap_led(23, 'on'); snap_led(18, 'off'); snap_led(24, 'off')
        if wiz: await light.turn_on(PilotBuilder(rgb=(255, 140, 0)))
    elif current_energy > cheap:
        print('Turn on everything now!')
        snap_led(24, 'on'); snap_led(18, 'off'); snap_led(23, 'on')
        if wiz: await light.turn_on(PilotBuilder(rgb=(255, 255, 224)))
    else:
        print('Turn on everything now! Even stuff you do not use.')
        snap_led(24, 'on'); snap_led(18, 'off'); snap_led(23, 'off')
        if wiz: await light.turn_on(PilotBuilder(rgb=(255, 255, 255)))

async def snap_error_wiz():
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(rgb=(0, 0, 255)))

def snap_check_average_price():
    avarage_part = 0.6666667
    if today_average > (very_expensive * avarage_part):
        print('Live in cave today')
        snap_led(25, 'on'); snap_led(8, 'off'); snap_led(7, 'off')
    elif today_average > (expensive * avarage_part):
        print('You can use one thing today')
        snap_led(25, 'on'); snap_led(8, 'on'); snap_led(7, 'off')
    elif today_average > (ok * avarage_part):
        print('Turn on some stuff today')
        snap_led(8, 'on'); snap_led(25, 'off'); snap_led(7, 'off')
    elif today_average > (cheap * avarage_part):
        print('Turn on everything today!')
        snap_led(7, 'on'); snap_led(25, 'off'); snap_led(8, 'on')
    else:
        print('Turn on everything today! Even stuff you do not use.')
        snap_led(7, 'on'); snap_led(25, 'off'); snap_led(8, 'off')

# Tibber API config
endpoint = 'https://api.tibber.com/v1-beta/gql'
headers = {
    'Authorization': f'Bearer {tibber_api_key}',
    'Content-Type': 'application/json'
}

query = """{
  viewer {
    homes {
      id
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

# Run intro
if led:
    snap_intro()

# Main loop
while True:
    try:
        r = requests.post(endpoint, json={'query': query}, headers=headers)
        data = r.json()['data']['viewer']['homes'][home_index]['currentSubscription']['priceInfo']
        current_energy = data['current']['energy']
        print('Current energy:', current_energy)

        today_prices = data['today']
        today_average = sum(hour['energy'] for hour in today_prices) / 24
        print('Today Average:', today_average)

        asyncio.run(snap_check_current_energy_price())
        snap_check_average_price()

        snap_led(16, "on")
        time.sleep(0.1)
        snap_led(16, "off")

        break
    except Exception as e:
        print("Error:", e)
        snap_led(16, "on")
        if wiz:
            asyncio.run(snap_error_wiz())
        time.sleep(10)

    time.sleep(60)
