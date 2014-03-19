#!/usr/bin/env python

"""raspitap.py: A Makey-Makey clone for Raspberry PI."""

import os
import json

from evdev import UInput, AbsInfo, ecodes as e

import RPi.GPIO as GPIO
import mpr121

# Use GPIO Interrupt Pin

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)

# Use mpr121 class for everything else

mpr121.TOU_THRESH = 0x30
mpr121.REL_THRESH = 0x33
mpr121.setup(0x5a)

# Set up event injection
ui = UInput()

# FIXME: needs a scheme to set these via config and more extensibly than a fixed length list
keys = [e.KEY_A, e.KEY_B, e.KEY_C, e.KEY_D, e.KEY_LEFT, e.KEY_UP, e.KEY_DOWN, e.KEY_RIGHT, e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4]

# Track touches
touches = [0,0,0,0,0,0,0,0,0,0,0,0];

while True:

	if (GPIO.input(7)): # Interupt pin is high
		pass
	else: # Interupt pin is low

		touchData = mpr121.readWordData(0x5a)

		for i in xrange(12):
			if (touchData & (1<<i)):
				if (touches[i] == 0):
					print( 'Pin ' + str(i) + ' was just touched')
					ui.write(e.EV_KEY, keys[i], 1) # key down
				touches[i] = 1;
			else:
				if (touches[i] == 1):
					print( 'Pin ' + str(i) + ' was just released')
					ui.write(e.EV_KEY, keys[i], 0) # key down
				touches[i] = 0
		ui.syn()
ui.close()
