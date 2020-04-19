#!/bin/bash
ffmpeg \
  -framerate 12 \
  -start_number 0 \
  -i slices/slice_%08d.png \
  -vcodec libx264 \
  -pix_fmt yuv420p \
  -preset veryslow \
  -tune zerolatency \
  april11.mp4

