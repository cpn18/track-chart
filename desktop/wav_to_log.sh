#!/bin/bash
# 20210424145628_left.wav

for f in *.wav; do
	y=`echo $f | cut -c 1-4`
	m=`echo $f | cut -c 5-6`
	d=`echo $f | cut -c 7-8`
	H=`echo $f | cut -c 9-10`
	M=`echo $f | cut -c 11-12`
	S=`echo $f | cut -c 13-14`

	echo ${y}-${m}-${d}T${H}:${M}:${S}Z WAV {\"class\": \"WAV\", \"file\": \"${f}\"} '*'
done
