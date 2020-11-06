#!/bin/bash

datadir=/root/gps-data

collect()
{
  ts=`date +%Y%m%d%H%M%S`
  arecord \
    -d 60 \
    --device=hw:CARD=Device,DEV=0 \
    --format S16_LE \
    --rate 44100 \
    -c1 ${datadir}/${ts}_left.wav &
  arecord \
    -d 60 \
    --device=hw:CARD=Device_1,DEV=0 \
    --format S16_LE \
    --rate 44100 \
    -c1 ${datadir}/${ts}_right.wav &
  wait
}

while true; do
	if [ `arecord -l | wc -l` -gt 1 ]; then
	    collect
	else
	    sleep 30
	fi
done
