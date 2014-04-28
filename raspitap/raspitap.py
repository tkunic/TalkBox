#!/usr/bin/env python

# TODO add basic input checking

import os
import json
from zipfile import ZipFile

NUMBER_OF_PINS = 12

class TalkBoxConf:

    def __init__(self):
        self.soundsets = {}

    def set_from_file(self, file_path):
        self.soundsets.clear()
        with ZipFile(file_path) as zfp:
            # use generator to filter out all files that aren not json
            for json_file in (filename for filename in zfp.namelist() if filename.lower().endswith('.json')):
                with zfp.open(json_file) as fp:
                    ss = SoundSet('.'.join(json_file.split('.')[0:-1]))
                    ss.from_json(fp.read())
                    self.add_soundset(ss)


    def write_to_file(self, file_path):
        with ZipFile(file_path, 'w') as zfp:
            for soundset_name, soundset in self.soundsets.iteritems():
                zfp.writestr(soundset_name+'.json', soundset.to_json())
                for pin_num in xrange(NUMBER_OF_PINS):
                    soundfile_path = soundset.get_pin(pin_num).get_soundfile()
                    if os.path.isfile(soundfile_path):
                        zfp.write(soundfile_path)

    def list_soundsets(self):
        return self.soundsets

    def add_soundset(self, soundset):
        self.soundsets[soundset.get_name()] = soundset

    def remove_soundset(self, soundset_name):
        del self.soundsets[soundset_name]

    def get_soundset(self, soundset_name):
        return self.soundsets[soundset_name]

class SoundSet:

    def __init__(self, name):
        self.name = name
        self.pinconfs = {}
        for pin_num in xrange(NUMBER_OF_PINS):
            self.pinconfs[pin_num] = PinConf()

    def to_json(self):
        result_map = {}
        for pin_num, pinconf in self.pinconfs.iteritems():
            result_map[pin_num] = {}
            soundfile_path = pinconf.get_soundfile() 
            result_map[pin_num]['soundfile_path'] = soundfile_path
            result_map[pin_num]['soundfile_name'] = os.path.basename(soundfile_path)

        return json.dumps(result_map)

    def from_json(self, json_string):
        for pin_num, entry in json.loads(json_string).iteritems():
            self.pinconfs[pin_num] = PinConf()
            self.pinconfs[pin_num].set_soundfile(entry['soundfile_name'])
            
    def get_name(self):
        return self.name

    def get_pin(self, pin_num):
        return self.pinconfs[pin_num]

class PinConf:
    def __init__(self):
        self.soundfile_path = ''

    def set_soundfile(self, soundfile_path):
        self.soundfile_path = soundfile_path

    def get_soundfile(self):
        return self.soundfile_path

    def set_soundsynth(self, text):
        """Synths speech from this text using espeak and writes result to a file."""
        pass
