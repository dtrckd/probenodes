#!/bin/bash

# scp the file from zombie-dust

PB_CPU="$(cat pb_cpu)"
PB_MEM="$(cat pb_mem)"

F="
HTTP/1.1 200 OK\n\n \
<!DOCTYPE html><html><body> \
    <pre>$PB_CPU \n $PB_MEM</pre> \
</body></html> \
"

echo -e "$F" > probe.html
P=
cp $P/probe.html /media/Synology/home/dulac/probe.html



SCRIPT="above script..."
#crontab -r # how to replace  cron ????

echo "* * * * * $SCRIPT" | crontab -

crontab -l

