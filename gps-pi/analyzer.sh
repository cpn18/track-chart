#!/bin/bash

port="$1"
output="$2"

while true; do
    timestamp=`date +%Y%m%d%H%M%S`
    ./analyzer.py \
	1> ${output}/analyzer_stdout_${timestamp}.log \
	2> ${output}/analyzer_stderr_${timestamp}.log
done
