# Snap
Code and build instructions for [Snap](https://www.instagram.com/p/CVXhBlCs5un/)

## Setup
Install [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on a Raspberry Pi

Buy some [LEDs, wires and a breadboard](https://www.instagram.com/p/CU1-_8KsBTz/). I only used the [breadboard](https://www.instagram.com/p/CU7GH0gMow4/) while building.

Connect the LEDs to the GPIO pins of your liking, you can see which one I used in my script.

Download [the script](snap.py) and put it in your home folder, for example /home/pi/.

Go to [Tibber](https://developer.tibber.com/settings/accesstoken) and get your Access Token.

Edit the downloaded script, and change YOUR-TOKEN-HERE to your Access Token.

If you have more than one home, change:
```
['homes'][0]
```
to reflect which home you are pulling data from. To see which home you want to use, go to [Tibbers Api Explorer](https://developer.tibber.com/explorer) and Load your personal token and simply run "Homes" in the drop down.

Open console and enter:
```
sudo nano /etc/rc.local
```
In /etc/rc.local you enter:
```
python /home/pi/snap.py
```
before exit 0, that will make the script run on startup.

Restart your Pi and press watch the lights.

## Learn and experiment

If you want to change your script [Tibber has an excellent playground here](https://developer.tibber.com/explorer).

And here you can read more about [GraphQL Concepts](https://developer.tibber.com/docs/guides/graphql-concepts).

That's basically all I used for reference making this project. Good luck!