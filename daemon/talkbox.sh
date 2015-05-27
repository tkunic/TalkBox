#! /bin/sh
# /etc/init.d/talkbox.sh
 
### BEGIN INIT INFO
# Provides: talkbox
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Simple script to start a program at boot
# Description: A simple script from www.stuffaboutcode.com which will start / stop a program a boot / shutdown.
### END INIT INFO

# Global commands and variables
PIDFILE=/var/tmp/talkboxd.pid
PYDAEMONLOC=/home/pi/TalkBox/talkbox.py
 
# Daemon control functions
case "$1" in
start)
echo "Starting TalkBox..."
# run application you want to start
python $PYDAEMONLOC &
echo "$!" >> $PIDFILE
;;
stop)
echo "Stopping TalkBox..."
# kill application you want to stop

while read line
do
    cur_pid=$line
    kill -9 $cur_pid
done < $PIDFILE
rm $PIDFILE
;;
*)
echo "Usage: /etc/init.d/talkbox.sh {start|stop}"
exit 1
;;
esac
 
exit 0
