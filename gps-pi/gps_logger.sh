#!/bin/bash

port="$1"
output="$2"

while true; do
	./gps_logger.py ${port} ${output} > ${output}/gps_stdout.log 1> ${output}/gps_stderr.log
done
