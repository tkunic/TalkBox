raspitap
========

A python library that simulates keypresses on input from MPR121.

The main intent is to compliment educational game development on the Raspberry Pi: In addition to building a game, students can now use a simple MPR121 chip to construct novel controllers and methods of input and interaction by making anything simulate a keypress.

The mpr121.py is derived from Scott Garner's [Beetbox](http://scott.j38.net/interactive/beetbox/) project, which is in turn based on [an Arduino example by Jim Lindblom](http://bildr.org/2011/05/mpr121_arduino/).

Hardware
--------
- [MPR121 Capacitive Touch Sensor Breakout Board](https://www.sparkfun.com/products/9695)
- [RaspberryPi](http://www.raspberrypi.org/)
- some headers and wires

Setup Instructions
------------------

``` bash
sudo apt-get install libgtk-3-dev python-smbus i2c-tools python-dev python-pip espeak
sudo apt-get update; sudo apt-get upgrade; sudo apt-get dist-upgrade
sudo pip install evdev
```
open /etc/modules and add:
```
i2c-bcm2708
i2c-dev
```

open /etc/modprobe.d/raspi-blacklist.conf and comment out:

`# blacklist i2c-bcm2708`

and reboot. To test, run:

`sudo i2cdetect -y 1`

And you should see the mpr121 chip as a device called '5a'.
