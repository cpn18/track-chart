#!/bin/bash

port="$1"
output="$2"

while true; do
	./web_server.py ${port} ${output} > ${output}/web_stdout.log 1> ${output}/web_stderr.log
done
