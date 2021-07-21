#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./lpcm_logger.py \
        ${port} \
	${output} \
	1> ${output}/lpcm_stdout_${timestamp}.log \
       	2> ${output}/lpcm_stderr_${timestamp}.log
done
