#!/bin/bash

./probenodes.py  &

while true ; do echo -e "$(probenodes.py html)" | nc -l -p 8000  ; done 
