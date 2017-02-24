#!/bin/bash

PORT="8000"
./probenodes.py  &

#while true ; do echo -e "$(probenodes.py html)" | nc -l -p $PORT; done 
socat TCP4-LISTEN:$PORT,fork EXEC:"./probenodes.py html"
