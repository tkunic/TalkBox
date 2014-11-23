import threading
import logging
import os

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
    def __init__(self, soundset_dir=os.path.join(conf_dir,'default'):
        self.soundset_dir = soundset_dir
        self.conf_file = os.path.join(soundset_dir, 'conf.json')
        try:
            with open(self.conf_file, 'r') as fin:
                self.conf = json.load(fin)
        except:
            logging.error('Failed to read the conf file at %s' % conf_file)
            self.play_sentence("Talk Box failed to load configuration. Please reboot or contact gamay lab.")

        self.name_file = self.conf.name
        self.name_sound = create_sound(self.name_file)

        self.pins = {}
        for i in xrange(1,num_pins + 1):
            pin_conf = self.conf[str(i)]
            filename = pin_conf['filename']

            self.pins[i] = {}
            self.pins[i]['filename'] = filename
            self.pins[i]['sound'] = self.create_sound(filename)

        self.play_name()

    def create_sound(self, sound_file):
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(1.0)
        return sound

    def get_pin_file(self, pin_num):
        return self.pins[pin_num]['filename']

    def play_pin(self, pin_num):
        self.pins[pin_num]['sound'].play()

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
    def __init__(self):
        self.sound_set = SoundSet() # create default soundset
        # Start button_worker thread
        self.button_thread = threading.Thread(name='button_worker', target=self.button_worker)
        self.button_thread.start()

    def GET(self):
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
</div>""" % (i, os.path.basename(self.sound_set.get_pin_file(i)) if self.sound_set.get_pin_file(i) != '' else "No File", ''.join(['pinfile', i])))

        result_list.append("""<input type="submit" value="Save" class="savebutton"/>
</form>
</body>
</html>""")
        return ''.join(result)

    def POST(self):
        # TODO: this is silly, but didn't find a better way quickly enough.
        x = web.input(pinfile1={},pinfile2={},pinfile3={},pinfile4={},pinfile5={},pinfile6={},pinfile7={},pinfile8={},pinfile9={},pinfile10={},pinfile11={},pinfile12={})
        for filefield in x.keys():
            # TODO: use os.path for most of this.
            input_filepath = x[filefield].filename.replace('\\', '/')
            input_filename = input_filepath.split('/')[-1]

            # Write the uploaded file to filedir
            if input_filename is not None and input_filename != '':
                # TODO: what if someone uploads blap.wav to pin 3 even though it
                # is already on pin 2 and the blap.wav files are different despite
                # the same name? Rename to blap(2).wav.
                file_destination_path = os.path.join(self.sound_set.get_dir(), input_filename)
                with open(file_destination_path, 'w') as fout:
                    fout.write(x.get(filefield).file.read())
                    fout.close()

            # TODO: this is ugly beyond words. Gets last number in 'pinfileX' string
            pin_num = re.compile('\d+').findall(filefield)[-1]
            self.update_pin_config(pin_num, file_destination_path)

        # TODO TODO TODO ============================================================
        # END RUNNING button_worker! (poison pill?)
        # START NEW button_worker!
        # TODO TODO TODO ============================================================

        # TODO: Indicate to user that update has been successful.

    def update_pin_config(self, pin_num, file_name):
        # Update the configuration file with the new filenames.
        try:
            with open(os.join(self.sound_set.get_dir(), 'conf.json'), 'w') as fout:
                json.dump(conf, fout, indent=4)

        except Exception as e:
            # TODO: actually display this in the browser as feedback to the user
            self.sound_set.play_sentence("ERROR: failed to write configuration")

        raise web.seeother('/')

    def button_worker(self, sound_set):
        while True:
            if not GPIO.input(7): # Interupt pin is low
                touchData = mpr121.readWordData(0x5a)
                for i in xrange(num_pins):
                    if (touchData & (1<<i)):
                        self.sound_set.play_pin(i + 1)

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

    # Init Web (which in turn inits buttons)
    # TODO: add further URLs, for example to test I2C and other statuses.
    urls = ('/', 'Upload')
    app = web.application(urls, globals())
    app.run()
