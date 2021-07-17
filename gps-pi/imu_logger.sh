#!/bin/bash

port="$1"
output="$2"

while true; do
	./imu_logger.py ${port} ${output} > ${output}/imu_stdout.log 1> ${output}/imu_stderr.log
done
