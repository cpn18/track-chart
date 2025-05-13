#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./simulator.py \
        ${port} \
	${output} \
	1> ${output}/sim_stdout_${timestamp}.log \
       	2> ${output}/sim_stderr_${timestamp}.log
done
