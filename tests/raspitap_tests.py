from nose.tools import *
from raspitap.raspitap import TalkBoxConf, SoundSet, PinConf

def setup():
	print "SETUP!"

def teardown():
	print "TEAR DOWN!"

def test_basic():
	print "DONE!"

def test_write_read_empty_TalkBoxConf():
    tbc1 = TalkBoxConf()
    soundset1 = SoundSet('soundset1')
    tbc1.add_soundset(soundset1)
    tbc1.write_to_file('/tmp/test.tbc')
    
    tbc2 = TalkBoxConf()
    tbc2.set_from_file('/tmp/test.tbc')

    gotten_soundset1 = tbc2.get_soundset('soundset1')

    assert gotten_soundset1.get_name() == soundset1.get_name()


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
