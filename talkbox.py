#!/usr/bin/env python

"""talkbox.py: Trigger script for the TalkBox."""

import os
import time

import pygame
import json
import math
import glob

import evdev
from asyncore import file_dispatcher, loop

import RPi.GPIO as GPIO
import mpr121

# Some constants
LMC = 0
RMC = 1
SCRU = 2
SCRD = 3

# Initialize the mouse - count on only one mouse being plugged in
paths = glob.glob('/dev/input/by-path/*-event-mouse')
dev = None
if(len(paths) > 0):
	dev = evdev.InputDevice(paths[0])
	print "Using device ", paths[0]

# Simplest to manage as globals in such a small script
sound_index = 0
volume_level = .60

def get_soundsets(soundset_dir):
	"Get relevant soundsets configurations contained in soundset_dir path."
	soundsets = []
	CONF_JSON = 'soundconf.json'
	soundset_dirs = ['/home/pi/TalkBox/sounds']

	for root, dirs, files in os.walk(soundset_dir):
		if CONF_JSON in files and not 'example' in root:
			soundconf = json.load(open(root + os.sep + CONF_JSON, 'r'))
			soundconf['rootdir'] = root
			soundsets.append(soundconf)
	soundsets.sort()
	return soundsets


def next_soundset():
	global sound_index
	sound_index = (sound_index + 1) % len(soundsets)
	sounds = extract_sound(soundsets[sound_index])
	soundset_filename = soundsets[sound_index]['rootdir'] + os.sep + soundsets[sound_index]['soundset_filename']
	create_sound(soundset_filename).play()
	return sounds

def prev_soundset():
	global sound_index
	sound_index = (sound_index - 1) % len(soundsets)
	sounds = extract_sound(soundsets[sound_index])
	soundset_filename = soundsets[sound_index]['rootdir'] + os.sep + soundsets[sound_index]['soundset_filename']
	create_sound(soundset_filename).play()
	return sounds

def extract_sound(soundset):
	sounds = {}
	for key, value in soundset['sounds'].iteritems():
		sound = create_sound(soundset['rootdir'] + os.sep + value['filename'])
		sounds[int(key)] = sound
	return sounds

def inc_volume(sounds):
	global volume_level
	volume_level = min(1.0, volume_level + 0.1)
	for sound in sounds.values():
		sound.set_volume(volume_level)
	pop_sound.set_volume(volume_level)
	pop_sound.play()
	return sounds

def dec_volume(sounds):
	global volume_level
	volume_level = max(0.0, volume_level - 0.1)
	for sound in sounds.values():
		sound.set_volume(volume_level)
	pop_sound.set_volume(volume_level)
	pop_sound.play()
	return sounds

def create_sound(sound_path):
	sound = pygame.mixer.Sound(sound_path)
	sound.set_volume(volume_level)
	return sound

# Use GPIO Interrupt Pin

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Use mpr121 class for everything else

mpr121.TOU_THRESH = 0x30
mpr121.REL_THRESH = 0x33
mpr121.setup(0x5a)

# User pygame for sounds

pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()


pop_sound = create_sound('/home/pi/TalkBox/sounds/pop.wav')
soundsets = get_soundsets('/home/pi/TalkBox/sounds')
# TODO soundsets = soundsets + get_soundsets('/path/to/USB/mount')
sounds = next_soundset()

def handleTouch(channel):
	touchData = mpr121.readWordData(0x5a)

	for i in xrange(12):
		if (touchData & (1<<i)):
			#print( 'Pin ' + str(i) + ' was just touched')
			sounds[i].play()
		else:
			pass

GPIO.add_event_detect(7, GPIO.FALLING, callback=handleTouch)

# Each click is two events (push down and push up). This is to ensure one action per two events.
rem_events = {LMC: 0, RMC: 0, SCRU: 0, SCRD: 0}

def handleMouse(events):
	global sounds
	global rem_events
	relevant_events = []
	try:
		for event in events:
			if event.code == evdev.ecodes.ecodes['BTN_LEFT']:
				rem_events[LMC] = rem_events[LMC] + 1
			elif event.code == evdev.ecodes.ecodes['BTN_RIGHT']:
				rem_events[RMC] = rem_events[RMC] + 1
			elif event.code == evdev.ecodes.ecodes['REL_WHEEL'] and event.value == 1:
				rem_events[SCRU] = rem_events[SCRU] + 1
			elif event.code == evdev.ecodes.ecodes['REL_WHEEL'] and event.value == -1:
				rem_events[SCRD] = rem_events[SCRD] + 1

		if (rem_events[LMC] > 1):
			sounds = prev_soundset()
			rem_events[LMC] = rem_events[LMC] % 2
		elif (rem_events[RMC] > 1):
			sounds = next_soundset()
			rem_events[RMC] = rem_events[RMC] % 2
		elif (rem_events[SCRD] > 1):
			sounds = dec_volume(sounds)
			rem_events[SCRD] = rem_events[SCRD] % 2
		elif (rem_events[SCRU] > 1):
			sounds = inc_volume(sounds)
			rem_events[SCRU] = rem_events[SCRU] % 2
	except:
		pass

class InputDeviceDispatcher(file_dispatcher):
	def __init__(self, device):
		self.device = device
		file_dispatcher.__init__(self, device)

	def recv(self, ign=None):
		return self.device.read()

	def handle_read(self):
		handleMouse(self.recv())

if (dev != None):
	InputDeviceDispatcher(dev)
	loop()
else:
	while True:
		# just a hacky way to run an infinite loop without 100% cpu usage
		time.sleep(9001)
