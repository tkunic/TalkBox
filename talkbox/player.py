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

volume_level = .60

class TBPlayer:
    def __init__(self):
        # Use GPIO Interrupt Pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Use mpr121 module for everything else
        mpr121.TOU_THRESH = 0x30
        mpr121.REL_THRESH = 0x33
        mpr121.setup(0x5a)
        
        # Use pygame for sounds
        pygame.mixer.pre_init(44100, -16, 12, 512)
        pygame.init() 

    def play_TalkBoxConf(self, tbc):
        pass
    
    def play_SoundSet(self, soundset):
        self.stop_SoundSet()
        # TODO set up sounds to be played by handleTouch
        GPIO.add_event_detect(7, GPIO.FALLING, callback=self.handleTouch)
    
    def stop_SoundSet(self):
        pass
    
    def handleTouch(channel):
        touchData = mpr121.readWordData(0x5a)
    
        for i in xrange(12):
            if (touchData & (1<<i)):
                #print( 'Pin ' + str(i) + ' was just touched')
                sounds[i].play()
            else:
                pass
    
    def play_sound(self, pygame_sound):
        pass
    
    def play_soundfile(self, filepath):
        pass
    
