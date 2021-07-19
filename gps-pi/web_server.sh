#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./web_server.py \
	${port} \
       	${output} \
       	1> ${output}/web_stdout_${timestamp}.log \
	2> ${output}/web_stderr_${timestamp}.log
done
