#!/bin/bash

output="$1"

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
    ./camera_logger.py \
	${output} \
	1>> ${output}/camera_stdout_${timestamp}.log \
       	2>> ${output}/camera_stderr_${timestamp}.log
done
