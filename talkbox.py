#!/usr/bin/env python

"""talkbox.py: Trigger script for the TalkBox."""

import pygame

import RPi.GPIO as GPIO
import mpr121
import re
import json

# Use GPIO Interrupt Pin

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)

# Use mpr121 class for everything else

mpr121.TOU_THRESH = 0x30
mpr121.REL_THRESH = 0x33
mpr121.setup(0x5a)

# User pygame for sounds

pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()

sounds = range(1, 13)

numpattern = re.compile('\d+')
conf = {}
with open('/home/pi/.tbconf/conf.json', 'r') as fin:
	conf = json.load(fin)
for pin in conf:
	print pin
	print numpattern.findall(pin)
	sounds[int(numpattern.findall(pin)[0]) - 1] = pygame.mixer.Sound(conf[pin])
	
for sound in sounds:
	sound.set_volume(1.0)

# Track touches

touches = [0,0,0,0,0,0,0,0,0,0,0,0];

while True:

	if (GPIO.input(7)): # Interupt pin is high
		pass
	else: # Interupt pin is low

		touchData = mpr121.readWordData(0x5a)

		for i in range(12):
			if (touchData & (1<<i)):

				if (touches[i] == 0):

					print( 'Pin ' + str(i) + ' was just touched')

					sounds[i].play()

				touches[i] = 1;
			else:
				if (touches[i] == 1):
					print( 'Pin ' + str(i) + ' was just released')
				touches[i] = 0;

