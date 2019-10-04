#!/bin/bash

#setup wifi
nmcli dev wifi hotspot ifname wlan0 ssid rpi-13 password "rpi-team13"

#run python code?
python3 /home/robot13/LED.py