import os
import time

import pygame
import json
import math
import glob
import re

import evdev
from asyncore import file_dispatcher, loop

import subprocess

try:
    import RPi.GPIO as GPIO
    import mpr121
except:
    print "not running on pi"

volume_level = .60
NUMBER_OF_PINS = 12

# TODO when installed on a rpi, remove the tk_
# TODO or just have warning box if you aren't on the pi or if you don't have a
# TODO mpr121 chip connected to GPIO

class TBPlayer:
    def __init__(self):
        try:
            # Use GPIO Interrupt Pin
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Use mpr121 module for everything else
            mpr121.TOU_THRESH = 0x30
            mpr121.REL_THRESH = 0x33
            mpr121.setup(0x5a)
        except:
            print "not running on pi"
        
        # Use pygame for sounds
        pygame.mixer.pre_init(22050, -16, 12, 512)
        pygame.init() 

    def set_TalkBoxConf(self, tbc):
        pass
    
    def play_SoundSet(self, soundset):
        self.stop_SoundSet()
        
        if (soundset == None):
            return
        
        self.sounds = []
        for i in range(12):
            soundstring = soundset.get_pin(i).get_soundstring()
            if os.path.exists(soundstring):
                sound = pygame.mixer.Sound(soundstring)
                sound.set_volume(volume_level)
                self.sounds.append(sound)
            else:
                filename = self.synth_soundfile(soundstring)
                sound = pygame.mixer.Sound(filename)
                sound.set_volume(volume_level)
                self.sounds.append(sound)

        GPIO.add_event_detect(7, GPIO.FALLING, callback=self.handleTouch)
        print ("playing soundset: " + soundset.get_name())
        global playing
        playing = True
    
    def stop_SoundSet(self):
        #tk _ GPIO.remove_event_detect(7)
        print("stopping soundset")
        global playing
        playing = False
    
    def handleTouch(self, channel):
        touchData = mpr121.readWordData(0x5a)
    
        for i in range(12):
            if (touchData & (1<<i)):
                #print( 'Pin ' + str(i) + ' was just touched')
                self.sounds[i].play()
            else:
                pass
    
    def play_soundstring(self, soundstring):
        # TODO? Implement cache table for sounds here with capacity 5 to avoid
        # reading from the disk all the time
        if soundstring is None or soundstring == '':
            return
        if os.path.exists(soundstring):
            subprocess.Popen(['aplay', soundstring])
        else:
            print "playing soundstring using espeak: " + soundstring
            tmpfile = '/tmp/espeak_buffer.wav'
            subprocess.call(['espeak', soundstring, '-w', tmpfile])
            subprocess.Popen(['aplay', tmpfile])
            
    def synth_soundfile(self, text):
        filename = "{0}/espeak_{1}.wav".format('/tmp', re.sub('[^\d\w]', '', text.encode('ascii', 'ignore')))
        subprocess.call(['espeak', text, '-w', filename, '&'])
        return filename
    
    def is_playing(self):
        #tk_ if this works use it, if not, keep playing var
        """if GPIO.gpio_event_added(7):
            return True
        else:
            return False"""
        return playing

playing = False
