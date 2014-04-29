from nose.tools import *
from raspitap.raspitap import TalkBoxConf, SoundSet, PinConf

import hashlib

def setup():
	print "SETUP!"

def teardown():
	print "TEAR DOWN!"

# TODO write a test for every action/scenario/way the controller/view will be using the model.

wav_path = 'tests/resources/file1.wav'

def partial_file_checksum(filename):
    """Calculates a sha256 checksum based on the first 1kb of the file for identity verification purposes."""
    return hashlib.sha256(open(filename, 'rb').read(1024)).digest()

def test_assinging_soundfile_to_pin():
    """Create new TalkBoxConf, assign it a SoundSet and assign that SoundSet a Pin."""
    tbc1 = TalkBoxConf()
    soundset_name = 'SoundSet Assigning Soundfile To Pin'
    soundset1 = SoundSet(soundset_name)
    tbc1.add_soundset(soundset1)

    tbc1.get_soundset(soundset_name).get_pin(1).set_soundfile(wav_path)

    assert_equal(tbc1.get_soundset(soundset_name).get_pin(1).get_soundfile(), wav_path)

def test_write_read_empty_TalkBoxConf():
    """Write and read an empty TalkBoxConf to disk."""
    tbc_path = '/tmp/test.tbc'
    tbc1 = TalkBoxConf()
    tbc1.write_to_file(tbc_path)
    
    tbc2 = TalkBoxConf()
    tbc2.set_from_file(tbc_path)

    assert_equal(tbc1.list_soundsets(), [])
    assert_equal(tbc1.list_soundsets(), tbc2.list_soundsets())


def test_write_read_wav_TalkBoxConf():
    """Write and read a TalkBoxConf with a sound file to disk."""
    tbc_path = '/tmp/test.tbc'
    tbc1 = TalkBoxConf()

    soundset1 = SoundSet('soundset1')
    tbc1.add_soundset(soundset1)
    soundset1.get_pin(1).set_soundfile(wav_path)
    assert_equal(soundset1.get_pin(1).get_soundfile(), wav_path)

    tbc1.write_to_file(tbc_path)
    
    tbc2 = TalkBoxConf()
    tbc2.set_from_file(tbc_path)

    gotten_wav_path = tbc2.get_soundset('soundset1').get_pin(1).get_soundfile()
    assert_equal(partial_file_checksum(gotten_wav_path), partial_file_checksum(wav_path))

# A reminder of what python testing looks like

@raises(TypeError, ValueError)
def test_raises_type_error():
    raise TypeError("This is ok")

@raises(Exception)
def test_raises_exception():
    raise Exception

def test_true():
    assert True == True
    assert False != True
