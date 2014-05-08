import os
import time

import pygame
import json
import math
import glob

import evdev
from asyncore import file_dispatcher, loop

#tk_import RPi.GPIO as GPIO
#tk_import mpr121

volume_level = .60
NUMBER_OF_PINS = 12

# TODO when installed on a rpi, remove the tk_
# TODO or just have warning box if you aren't on the pi or if you don't have a
# TODO mpr121 chip connected to GPIO

class TBPlayer:
    def __init__(self):
        # Use GPIO Interrupt Pin
        #tk_GPIO.setmode(GPIO.BOARD)
        #tk_GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Use mpr121 module for everything else
        #tk_mpr121.TOU_THRESH = 0x30
        #tk_mpr121.REL_THRESH = 0x33
        #tk_mpr121.setup(0x5a)
        
        # Use pygame for sounds
        pygame.mixer.pre_init(44100, -16, 12, 512)
        pygame.init() 

    def play_TalkBoxConf(self, tbc):
        pass
    
    def play_SoundSet(self, soundset):
        self.stop_SoundSet()
        
        sounds = []
        for i in range(12):
            sound_path = soundset.get_pin(i).get_soundfile()
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume_level)
            sounds.append(sound)

        GPIO.add_event_detect(7, GPIO.FALLING, callback=self.handleTouch)
    
    def stop_SoundSet(self):
        GPIO.remove_event_detect(7)
    
    def handleTouch(channel):
        touchData = mpr121.readWordData(0x5a)
    
        for i in range(12):
            if (touchData & (1<<i)):
                #print( 'Pin ' + str(i) + ' was just touched')
                sounds[i].play()
            else:
                pass
    
    def play_soundfile(self, filepath):
        # TODO? Implement cache table for sounds here with capacity 5 to avoid
        # reading from the disk all the time
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(volume_level)
        sound.play()
    
    def is_playing(self):
        #tk_ if this works use it, if not, keep playing var
        """if GPIO.gpio_event_added(7):
            return True
        else:
            return False"""
        global playing
        if not playing:
            playing = True
            return False
        else:
            playing = False
            return True

playing = False