#!/usr/bin/env python

# TODO add basic input checking, as it stands, this is a very gullible module.
# TODO also, kinda ugly code, refactor a bit, add comments and docstrings.

import os
from os.path import basename
import json
from zipfile import ZipFile
import tempfile

NUMBER_OF_PINS = 12

class TalkBoxConf:

    def __init__(self):
        self.soundsets = []

    def set_from_file(self, file_path):
        """ Given a file_path to a *.tbc archive (a zipfile with soundfiles
        and a metadata.json file assigning them to soundsets and pins),
        load its contents into this TalkBoxConf."""

        # To avoid more complicated solutions, extracts the *.tbc archive to tempfile.mkdtemp('tbc') that starts with 'tbc'. Remember to delete when done.
        self.tmpdir = tempfile.mkdtemp(prefix='tbc')

        with ZipFile(file_path) as zfp:
            with zfp.open('metadata.json') as metadatafp:
                metadata = json.load(metadatafp)
                # each soundset entry in metadata contains the 'name' and pin numbers as keys
                self.soundsets = []
                for ss_md in metadata:
                    soundset = SoundSet(ss_md['name'])
                    # FIXME BAD: why should TalkBoxConf know how many pins there are?
                    for i in xrange(NUMBER_OF_PINS):
                        soundfile_path = ss_md[str(i)]['soundfile']
                        if soundfile_path is not None and soundfile_path != '':
                            soundset.get_pin(i).set_soundfile(zfp.extract(soundfile_path, self.tmpdir))
                    self.soundsets.append(soundset)

    def write_to_file(self, filename):
        """ Writes representation of self to a *.tbc archive """
        result = []
        with ZipFile(filename, 'w') as zfp:
            for soundset in self.soundsets:
                soundset_result = {'name': soundset.get_name()}
                # FIXME BAD: NUMBER_OF_PINS shouldn't be a concern of TalkBoxConf
                for i in xrange(NUMBER_OF_PINS):
                    soundset_result[i] = {'soundfile': basename(soundset.get_pin(i).get_soundfile())}
                for resource_path in soundset.get_resource_paths():
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
        del soundset

    def get_soundset(self, soundset_name):
        for soundset in self.soundsets:
            if soundset.get_name() == soundset_name:
                return soundset

class SoundSet:

    def __init__(self, name):
        self.name = name
        self.pinconfs = {}
        for pin_num in xrange(NUMBER_OF_PINS):
            self.pinconfs[pin_num] = PinConf()

    def get_name(self):
        return self.name

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

    def set_soundfile(self, soundfile_path):
        self.soundfile_path = soundfile_path

    def get_soundfile(self):
        return self.soundfile_path

    def set_soundsynth(self, text):
        """Synths speech from this text using espeak and writes result to a file."""
        pass
