#!/usr/bin/env python

import threading
import logging
import os
import subprocess

import re
import json

import pygame
import web

import RPi.GPIO as GPIO
import mpr121


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

conf_dir = '/home/pi/TalkBox/conf'
num_pins = 12 # FIXME: kinda stuck at 12 due to Upload.POST

class SoundSet():
    """Contains one pin to soundfile mapping."""
    def __init__(self, soundset_dir=os.path.join(conf_dir,'default')):
        self.soundset_dir = soundset_dir
        self.conf_file = os.path.join(soundset_dir, 'conf.json')
        self.conf = {}
        try:
            with open(self.conf_file, 'r') as fin:
                self.conf = json.load(fin)
        except:
            logging.error('Failed to read the conf file at %s' % self.conf_file)
            self.play_sentence("Talk Box failed to load configuration. Please reboot or contact gamay lab.")
            exit(1)

        self.name_file = self.conf['name']
        self.name_sound = self.create_sound(self.name_file)

        self.pins = {}
        for i in xrange(1,num_pins + 1):
            pin_conf = self.conf[str(i)]
            filename = pin_conf['filename']
            self.pins[i] = {}
            self.pins[i]['filename'] = filename
            if filename != "":
                self.pins[i]['sound'] = self.create_sound(filename)
            else:
                self.pins[i]['sound'] = None

        self.play_name()

    def create_sound(self, sound_file):
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(1.0)
        return sound

    def get_pin_file(self, pin_num):
        return self.pins[pin_num]['filename']

    def play_pin(self, pin_num):
        sound = self.pins[pin_num]['sound']
        if sound:
            sound.play()
        else:
            logging.warning("Sound not set for pin %d" % pin_num)

    def get_name_file(self):
        return self.name_file

    def play_name(self):
        self.name_sound.play()

    def get_dir(self):
        return self.soundset_dir

    def play_sentence(self, sentence):
        sentence_file = '/tmp/tbsentence.wav'
        subprocess.Popen(['espeak', '"', sentence, '"', '-w', sentence_file], stdout=subprocess.PIPE)
        self.create_sound(sentence_file).play()


class Upload:
    def GET(self):
        global sound_set
        web.header("Content-Type", "text/html; charset=utf-8")

        # TODO: Migrate to web.py templates
        result_list = []
        result_list.append("""<html>
<head>
    <link href="/static/style.css" type="text/css" rel="stylesheet">
</head>
<body>
<img src="static/talkbox_logo.png" id="talkboxlogo">
<form method="POST" enctype="multipart/form-data" action="">\n""")

        for i in xrange(1, num_pins + 1):
            result_list.append("""<div class="pinrow">
    <div class="pinnumber float-left">%d</div>
    <div class="filename float-left">%s</div>
    <div class="uploadbutton float-left">+<input type="file" name="%s" accept="audio/*" /></div>
</div>""" % (i, os.path.basename(sound_set.get_pin_file(i)) if sound_set.get_pin_file(i) != '' else "No File", ''.join(['pinfile', str(i)])))

        result_list.append("""<input type="submit" value="Save" class="savebutton"/>
</form>
</body>
</html>""")
        return ''.join(result_list)

    def POST(self):
        global sound_set
        # TODO: this is silly, but didn't find a better way quickly enough.
        x = web.input(pinfile1={},pinfile2={},pinfile3={},pinfile4={},pinfile5={},pinfile6={},pinfile7={},pinfile8={},pinfile9={},pinfile10={},pinfile11={},pinfile12={})
        for filefield in x.keys():
            # TODO: use os.path for most of this.
            input_filepath = x[filefield].filename.replace('\\', '/')
            input_filename = input_filepath.split('/')[-1]

            # Write the uploaded file to filedir
            file_destination_path = ''
            if input_filename is not None and input_filename != '':
                # TODO: what if someone uploads blap.wav to pin 3 even though it
                # is already on pin 2 and the blap.wav files are different despite
                # the same name? Rename to blap(2).wav.
                file_destination_path = os.path.join(sound_set.get_dir(), input_filename)
                with open(file_destination_path, 'w') as fout:
                    fout.write(x.get(filefield).file.read())
                    fout.close()

            if file_destination_path != '':
                # TODO: this is ugly beyond words. Gets last number in 'pinfileX' string
                pin_num = re.compile('\d+').findall(filefield)[-1]
                self.update_pin_config(pin_num, file_destination_path)

        # FIXME: Ensure no sounds are played while this is being changed.
        sound_set = SoundSet()

        # TODO: Indicate to user that update has been successful.
        raise web.seeother('/')

    def update_pin_config(self, pin_num, file_name):
        # Update the configuration file with the new filenames.
        try:
            conf_file = os.path.join(sound_set.get_dir(), 'conf.json')
            conf = None;

            # Get current contents of config file
            with open(conf_file, 'r') as fin:
                conf = json.load(fin)

            # Write updated config back
            with open(conf_file, 'w') as fout:
                conf[str(pin_num)]['filename'] = file_name
                json.dump(conf, fout, indent=4)

        except Exception as e:
            logging.error("ERROR: failed to write configuration due to: '%s'" % e.message)
            # TODO: actually display this in the browser as feedback to the user
            sound_set.play_sentence("ERROR: failed to write configuration")

class TalkBoxWeb(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

def button_worker():
    while True:
        if not GPIO.input(7) and not pygame.mixer.get_busy(): # Interupt pin is low and no sound is playing
            touchData = mpr121.readWordData(0x5a)
            for i in xrange(num_pins):
                if (touchData & (1<<i)):
                    sound_set.play_pin(i + 1)

if __name__ == "__main__":
    # Init GPIO Interrupt Pin
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.IN)

    # Init mpr121 touch sensor
    mpr121.TOU_THRESH = 0x30
    mpr121.REL_THRESH = 0x33
    mpr121.setup(0x5a)

    # Init Pygame
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.init()

    # FIXME: shouldn't be global, but short on time
    sound_set = SoundSet()
    button_thread = None

    # Init button worker thread
    button_thread = threading.Thread(name='button_worker', target=button_worker)
    button_thread.start()

    # Init Web (which in turn inits buttons)
    # TODO: add further URLs, for example to test I2C and other statuses.
    urls = ('/', 'Upload')
    app = TalkBoxWeb(urls, globals())
    app.run(port=80)

