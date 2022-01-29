import RPi.GPIO as GPIO
import requests
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def snap_intro():
  # red
  snap_led(18,"on")
  time.sleep(.5)
  snap_led(18,"off")
  # yellow
  snap_led(23,"on")
  time.sleep(.5)
  snap_led(23,"off")
  # green
  snap_led(24,"on")
  time.sleep(.5)
  snap_led(24,"off")
  # red 2
  snap_led(25,"on")
  time.sleep(.5)
  snap_led(25,"off")
  # yellow 2
  snap_led(8,"on")
  time.sleep(.5)
  snap_led(8,"off")
  # green 2
  snap_led(7,"on")
  time.sleep(.5)
  snap_led(7,"off")
  # blue
  snap_led(16,"on")
  time.sleep(.5)
  snap_led(16,"off")

def snap_led(pin,state):
  GPIO.setup(pin,GPIO.OUT)
  if state == 'on':
    # print str(pin) + " on"
    GPIO.output(pin,GPIO.HIGH)
  else:
    # print str(pin) + " off"
    GPIO.output(pin,GPIO.LOW)

def snap_check_current_energy_price():
  if current_energy > very_expensive:
    print('Live in cave now')
    snap_led(18,'on')
    snap_led(23,'off')
    snap_led(24,'off')
  elif current_energy > expensive:
    print('You can use one thing now')
    snap_led(18,'on')
    snap_led(23,'on')
    snap_led(24,'off')
  elif current_energy > ok:
    print('Turn on some stuff now')
    snap_led(23,'on')
    snap_led(18,'off')
    snap_led(24,'off')
  elif current_energy > cheap:
    print('Turn on everything now!')
    snap_led(24,'on')
    snap_led(18,'off')
    snap_led(23,'on')
  else:
    print('Turn on everything now! Even stuff you do not use.')
    snap_led(24,'on')
    snap_led(18,'off')
    snap_led(23,'off')

def snap_check_average_price():
  avarage_part = 0.6666667;
  if today_average > (very_expensive*avarage_part):
    print('Live in cave today')
    snap_led(25,'on')
    snap_led(8,'off')
    snap_led(7,'off')
  elif today_average > (expensive*avarage_part):
    print('You can use one thing today')
    snap_led(25,'on')
    snap_led(8,'on')
    snap_led(7,'off')
  elif today_average > (ok*avarage_part):
    print('Turn on some stuff today')
    snap_led(8,'on')
    snap_led(25,'off')
    snap_led(7,'off')
  elif today_average > (cheap*avarage_part):
    print('Turn on everything today!')
    snap_led(7,'on')
    snap_led(25,'off')
    snap_led(8,'on')
  else:
    print('Turn on everything today! Even stuff you do not use.')
    snap_led(7,'on')
    snap_led(25,'off')
    snap_led(8,'off')

endpoint = 'https://api.tibber.com/v1-beta/gql'
headers = {
  'Authorization': 'Bearer 5ntXzdGSAFkRj138j0v7O8T6-6hEOYyy6g7-FGSdIAQ',
  'Content-Type': 'application/json'
}

very_expensive = 3 # only red, under this = orange and red
expensive = 2 # orange and red, under this = orange
ok = 1 # only orange, under this = green and orange
cheap = .5 # green and orange, under this = only green

query = """{
  viewer {
    homes {
      id
      currentSubscription{
        priceInfo{
          current{
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
}
"""

snap_intro()

while True:
  try:
    r = requests.post(endpoint, json={'query': query}, headers=headers)

    current_energy = (r.json()['data']['viewer']['homes'][1]['currentSubscription']['priceInfo']['current']['energy'])
    print('Current energy: ' + str(current_energy))

    today_average_hours = (r.json()['data']['viewer']['homes'][1]['currentSubscription']['priceInfo']['today'])
    tmp_average = 0
    today_average = 0
    for hour in today_average_hours:
      tmp_hour = (hour['energy'])
      tmp_average = tmp_average + tmp_hour
    today_average = tmp_average / 24
    print('Today Average: ' + str(today_average))

    snap_check_current_energy_price()
    snap_check_average_price()

    snap_led(16,"on")
    time.sleep(.1)
    snap_led(16,"off")

    time.sleep(60)
  except:
    snap_led(16,"on")
    time.sleep(60)
