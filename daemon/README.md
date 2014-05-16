Turn TalkBox into a daemon
==========================

This are instructions to make TalkBox start up when your Pi boots:

Make sure the TalkBox folder is in /home/pi/

Move the talkbox.sh script into /etc/init.d:

```
sudo cp talkbox.sh /etc/init.d
```

To actually add it to rc.d directories, run:

```
sudo update-rc.d talkbox.sh defaults
```



And you are done!

In case you make modifications to TalkBox, run:
```
sudo /etc/init.d/talkbox.sh stop; sudo /etc/init.d/talkbox.sh start;
```

or just reboot the Pi.


Instructions are based on:
http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
