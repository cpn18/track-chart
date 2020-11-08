#!/bin/bash
if [ "$1" == "" ]; then
	echo "USGAGE: $0 output_file"
	exit 1
fi

ffmpeg \
  -framerate 12 \
  -start_number 0 \
  -i slices/slice_%08d.png \
  -vcodec libx264 \
  -pix_fmt yuv420p \
  -preset veryslow \
  -tune zerolatency \
  ${1}

