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

if [ `arecord -l | wc -l` -gt 1 ]; then
    collect
    retval=0
else
    retval=1
fi

exit ${retval}
