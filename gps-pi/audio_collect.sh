#!/bin/bash

outputdir=$1
timestamp=$2

collect()
{
  arecord \
    -d 60 \
    --device=hw:CARD=Device,DEV=0 \
    --format S16_LE \
    --rate 44100 \
    -c1 ${outputdir}/${timestamp}_left.wav &
  arecord \
    -d 60 \
    --device=hw:CARD=Device_1,DEV=0 \
    --format S16_LE \
    --rate 44100 \
    -c1 ${outputdir}/${timestamp}_right.wav &
  wait
}

if [ `arecord -l | wc -l` -gt 1 ]; then
    collect
    retval=0
else
    retval=1
fi

exit ${retval}
