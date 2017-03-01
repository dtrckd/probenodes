#!/bin/bash
 
#
# print total CPU usage in percent of all available users
# but skips the ones with a CPU usage of zero
#
# to sort by CPU usage, pipe the output to 'sort -k2 -nr'
#

set -e

OWN=$(id -nu)
TEAM='ama'
TASK="$1"
if [ "$TASK" == "mem" ]; then
    KPT='NR>7 { sum += $10; } END { print user, sum; }'
else # "cpu"
    KPT='NR>7 { sum += $9; } END { print user, sum; }'
    #KPT='NR>7 { sum += $9; } END { if (sum > 0.0) print user, sum; }'
fi

for USER in $(getent passwd |  grep "/$TEAM/" | awk -F ":" '{print $1}' | sort -u)
do
    # print other user's CPU usage in parallel but skip own one because
    # spawning many processes will increase our CPU usage significantly
    if [ "$USER" = "$OWN" ]; then continue; fi
    if [ ! -d /home/$TEAM/$USER ]; then continue; fi
    (top -b -n 1 -u "$USER" | awk -v user=$USER "$KPT") &
done
wait

# print own CPU usage after all spawned processes completed
top -b -n 1 -u "$OWN" | awk -v user=$OWN "$KPT"


if [ "$TASK" == "mem" ]; then
    # Get average Swap
    swp=$(free -m | grep Swap | awk '{print $3}')
    echo "scale=1; $swp / 1000" | bc -l
else
    # Get average Load
    cat /proc/loadavg | awk '{print $1}'
fi

# Get swap usage by process
# confident ? see smem...
#for file in /proc/*/status ; do awk '/VmSwap|Name/{printf $2 " " $3}END{ print ""}' $file; done | sort -k 2 -n -r 
