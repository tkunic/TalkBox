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

        # To avoid more complicated solutions, extracts the *.tbc archive to tempfile.mkdtemp('tbc') that starts with 'tbc'. Remember to delete when done.
        # remove all other temp files.
        for path in os.listdir('/tmp/'):
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
                        soundfile_path = ss_md[str(i)]['soundfile']
                        if soundfile_path is not None and soundfile_path != '':
                            filename = zfp.extract(soundfile_path, tmpdir)
                            soundset.get_pin(i).set_soundfile(filename)
                            if re.search('espeak_.*', filename) is not None:
                                soundstring = ss_md[str(i)]['soundstring']
                            else:
                                soundstring = filename
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
                    soundfile = basename(soundset.get_pin(i).get_soundfile())
                    soundstring = soundset.get_pin(i).get_soundstring()
                    print soundfile, soundstring
                    soundset_result[i] = {
                                          'soundfile': soundfile,
                                          'soundstring': soundstring
                                          }
                for resource_path in soundset.get_resource_paths():
                    try:
                        zfp.getinfo(basename(resource_path))
                    except:
                        zfp.write(resource_path, basename(resource_path))
                result.append(soundset_result)
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
            soundfile_path = pin_conf.get_soundfile()
            if os.path.exists(soundfile_path):
                result.append(os.path.abspath(soundfile_path))
            elif soundfile_path is not None and soundfile_path != '':
                raise Exception("Unknown resource: " + soundfile_path)
        return result
                

class PinConf:
    def __init__(self):
        self.soundfile_path = ''
        self.soundstring = ''

    def set_soundstring(self, soundstring):
        self.soundstring = soundstring
    
    def get_soundstring(self):
        if self.soundstring == "":
            return self.soundfile_path
        else:
            return self.soundstring

    def set_soundfile(self, soundfile_path):
        self.soundfile_path = soundfile_path

    def get_soundfile(self):
        if os.path.exists(self.soundfile_path):
            return self.soundfile_path
        elif self.soundstring != "":
            # if soundstring isn't a filename, synths speech from this text using espeak and returns filepath to synthesized sound."""
            return self.synth_soundfile(self.soundstring)
        else:
            return ''

    def synth_soundfile(self, text):
        filename = "{0}/espeak_{1}.wav".format(tmpdir, re.sub('[^\d\w]', '', text.encode('ascii', 'ignore')))
        subprocess.call(['espeak', text, '-w', filename])
        return filename
