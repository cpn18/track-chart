#!/bin/bash

outputdir=$1
timestamp=$2

if [ "$3" == "" ]; then
  args="--format S16_LE --rate=44100 --channels=1 --duration=60"
else
  args=$3
fi

collect()
{
  if [ `echo ${args} | grep -c "channels=2"` -eq 1 ]; then
      arecord \
        --device=hw:CARD=Device,DEV=0 \
        ${args} \
        ${outputdir}/${timestamp}_stereo.wav
  else
      arecord \
        --device=hw:CARD=Device,DEV=0 \
        ${args} \
        ${outputdir}/${timestamp}_left.wav &
      arecord \
        --device=hw:CARD=Device_1,DEV=0 \
        ${args} \
        ${outputdir}/${timestamp}_right.wav &
      wait
  fi
}

if [ `arecord -l | wc -l` -gt 1 ]; then
    collect
    retval=0
else
    retval=1
fi

exit ${retval}
