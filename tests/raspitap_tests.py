from nose.tools import *
from raspitap.raspitap import TalkBoxConf, SoundSet, PinConf

def setup():
	print "SETUP!"

def teardown():
	print "TEAR DOWN!"

# TODO write a test for every action/scenario/way the controller/view will be using the model.

def test_assinging_soundfile_to_pin():
    tbc1 = TalkBoxConf()
    soundset1 = SoundSet('SoundSet Assigning Soundfile To Pin')

    wav_path = 'tests/file1.wav'
    soundset1.get_pin(1).set_soundfile(wav_path)

    assertEquals(soundset1.get_pin(1).get_soundfile(), wav_path)

    tbc1_filepath = '/tmp/test_assign_soundfile.tbc'
    tbc1.write_to_file(tbc1_filepath)

    tbc1.add_soundset(soundset1)

    

def test_write_read_empty_TalkBoxConf():
    tbc1 = TalkBoxConf()
    soundset1 = SoundSet('soundset1')
    tbc1.add_soundset(soundset1)
    tbc1.write_to_file('/tmp/test.tbc')
    
    tbc2 = TalkBoxConf()
    tbc2.set_from_file('/tmp/test.tbc')

    gotten_soundset1 = tbc2.get_soundset('soundset1')

    assert_equal(gotten_soundset1.get_name(), soundset1.get_name())

def test_write_read_wav_TalkBoxConf():
    wav_path = 'tests/file1.wav'
    tbc1 = TalkBoxConf()

    soundset1 = SoundSet('soundset1')
    soundset1.get_pin(1).set_soundfile(wav_path)
    assert_equal(soundset1.get_pin(1).get_soundfile(), wav_path)

    tbc1.add_soundset(soundset1)
    tbc1.write_to_file('/tmp/test.tbc')
    
    tbc2 = TalkBoxConf()
    tbc2.set_from_file('/tmp/test.tbc')

    gotten_wav_path = tbc2.get_soundset('soundset1').get_pin(1).get_soundfile()
    assert_equal(gotten_wav_path, wav_path)

# Some temporary tests to remind myself what python testing looks like

@raises(TypeError, ValueError)
def test_raises_type_error():
    raise TypeError("This is ok")

@raises(Exception)
def test_raises_exception():
    raise Exception

def test_true():
    assert True == True
    assert False != True
