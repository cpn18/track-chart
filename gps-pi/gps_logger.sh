#!/bin/bash

port="$1"
output="$2"

function clean_children() {
    jobs=$(jobs -pr)
    while [ -n "${jobs[@]}" ]; 
    do
        for j in "${jobs[@]}"
        do
            kill -SIGINT $j
        done
        echo -e "wrapper killed jobs: ${jobs[@]}\n"
    done
    exit 0
}
trap clean_children SIGINT

while true; do
    timestamp=`date +%Y%m%d%H`
    ./gps_logger.py \
        ${port} \
	${output} \
	1>> ${output}/gps_stdout_${timestamp}.log \
       	2>> ${output}/gps_stderr_${timestamp}.log
done
