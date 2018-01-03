
#!/bin/bash

pid1=$(ps -u | grep "./probenodes.py$" | tr -s ' ' | cut  -d ' ' -f 2 )
pid2=$(ps -u | grep "socat.*probenodes" | tr -s ' ' | cut  -d ' ' -f 2 )

echo "pid ot kill: $pid1 $pid12"

kill -9  "$pid1" "$pid2"
