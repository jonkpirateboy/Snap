# Snap
Code and build instructions for [Snap](https://www.instagram.com/p/CVXhBlCs5un/)

Install [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on a Raspberry Pi

Buy some LEDs

Download [the script](snap.py) and put it in your home folder, /home/pi/

Open console and enter
```
sudo nano /etc/rc.local
```
In /etc/rc.local you enter 
```
python /home/pi/snap.py
```
before exit 0, that will make the script run on startup

Restart your Pi and press watch the lights.