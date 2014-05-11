#!/usr/bin/env python

# TODO add basic input checking, as it stands, this is a very gullible module.
# TODO also, kinda ugly code, refactor a bit, add comments and docstrings.

import os
from os.path import basename
import subprocess
import tempfile
import shutil

import re
import json
from zipfile import ZipFile

NUMBER_OF_PINS = 12
TMPDIR_PREFIX = "tbc_"
tmpdir = None

class TalkBoxConf:

    def __init__(self):
        self.soundsets = []

    def set_from_file(self, file_path):
        """ Given a file_path to a *.tbc archive (a zipfile with soundfiles
        and a metadata.json file assigning them to soundsets and pins),
        load its contents into this TalkBoxConf."""

        # To avoid more complicated solutions, extracts the *.tbc archive to temporary dir.
        for path in os.listdir('/tmp/'):
            # remove leftover temporary directories
            if re.search('^' + TMPDIR_PREFIX, path):
                try:
                    shutil.rmtree('/tmp/' + path)
                except:
                    print "deleting {0} failed.".format('/tmp/'+path)
        global tmpdir
        tmpdir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX)

        with ZipFile(file_path) as zfp:
            with zfp.open('metadata.json') as metadatafp:
                metadata = json.load(metadatafp)
                # each soundset entry in metadata contains the 'name' and pin numbers as keys
                self.soundsets = []
                for ss_md in metadata:
                    soundset = SoundSet(ss_md['name'])
                    # FIXME BAD: why should TalkBoxConf know how many pins there are?
                    for i in range(NUMBER_OF_PINS):
                        soundstring = ss_md[str(i)]['soundstring']
                        if soundstring.lower().endswith(".wav"):
                            filename = zfp.extract(soundstring, tmpdir)
                            soundset.get_pin(i).set_soundstring(filename)
                        else:
                            soundset.get_pin(i).set_soundstring(soundstring)
                    self.soundsets.append(soundset)

    def write_to_file(self, filename):
        """ Writes representation of self to a *.tbc archive """
        result = []
        with ZipFile(filename, 'w') as zfp:
            for soundset in self.soundsets:
                soundset_result = {'name': soundset.get_name()}
                # FIXME BAD: NUMBER_OF_PINS shouldn't be a concern of TalkBoxConf
                for i in range(NUMBER_OF_PINS):
                    soundstring = soundset.get_pin(i).get_soundstring()
                    if os.path.exists(soundstring):
                        soundstring = basename(soundset.get_pin(i).get_soundstring())
                    soundset_result[i] = {'soundstring': soundstring}
                result.append(soundset_result)
                for resource_path in soundset.get_resource_paths():
                    try:
                        zfp.getinfo(basename(resource_path))
                    except:
                        zfp.write(resource_path, basename(resource_path))
            json_string = json.dumps(result, sort_keys=True, indent=4)
            zfp.writestr('metadata.json', json_string)

    def list_soundsets(self):
        return self.soundsets

    def add_soundset(self, soundset):
        self.soundsets.append(soundset)

    def remove_soundset(self, soundset_name):
        soundset = self.get_soundset(soundset_name)
        self.soundsets.remove(soundset)

    def get_soundset(self, soundset_name):
        for soundset in self.soundsets:
            if soundset.get_name() == soundset_name:
                return soundset

class SoundSet:

    def __init__(self, name):
        self.name = name
        self.pinconfs = {}
        for pin_num in range(NUMBER_OF_PINS):
            self.pinconfs[pin_num] = PinConf()

    def get_name(self):
        return self.name
    
    def set_name(self, new_name):
        self.name = new_name

    def get_pin(self, pin_num):
        return self.pinconfs[pin_num]

    def get_resource_paths(self):
        """Returns a list of paths to resources used by this SoundSet."""
        result = []
        for pin_num, pin_conf in self.pinconfs.iteritems():
            soundstring = pin_conf.get_soundstring()
            if os.path.exists(soundstring):
                result.append(os.path.abspath(soundstring))
        return result
                

class PinConf:
    def __init__(self):
        self.soundstring = ''

    def set_soundstring(self, soundstring):
        self.soundstring = soundstring
    
    def get_soundstring(self):
        return self.soundstring

    def synth_soundfile(self, text):
        filename = "{0}/espeak_{1}.wav".format(tmpdir, re.sub('[^\d\w]', '', text.encode('ascii', 'ignore')))
        subprocess.call(['espeak', text, '-w', filename])
        return filename
