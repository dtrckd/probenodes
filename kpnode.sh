
#!/bin/bash

pid=$(ps -u | grep "./probenodes.py$" | tr -s ' ' | cut  -d ' ' -f 2 )

kill $pid 
