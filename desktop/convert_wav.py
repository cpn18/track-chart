#!/usr/bin/env python3
"""
Convert Stereo to/from Mono WAV files

WARNING: When converting two mono files to stereo, this
         program does not do any time code correction
"""
import sys
import wave


def mono_to_stereo(left_in, right_in, stereo_out):
    """ Convert Two Mono Files to One Stereo File """
    with wave.open(stereo_out, "wb") as stereo_channel:
        with wave.open(left_in, "rb") as left_channel:
            with wave.open(right_in, "rb") as right_channel:
                params = left_channel.getparams()
                params = right_channel.getparams()
                print(params)
                output_params = (
                    2, # Channels
                    params.sampwidth,
                    params.framerate,
                    params.nframes,
                    params.comptype,
                    params.compname
                )
                stereo_channel.setparams(output_params)
                for _i in range(params.nframes):
                    left_data = left_channel.readframes(1)
                    right_data = right_channel.readframes(1)
                    stereo_data = bytearray(left_data) + bytearray(right_data)
                    stereo_channel.writeframesraw(stereo_data)

def stereo_to_mono(stereo_in, left_out, right_out):
    """ Convert One Stereo File to Two Mono Files """
    with wave.open(left_out, "wb") as left_channel:
        with wave.open(right_out, "wb") as right_channel:
            with wave.open(stereo_in, "rb") as stereo_channel:
                params = stereo_channel.getparams()
                print(params)
                output_params = (
                    1, # Channels
                    params.sampwidth,
                    params.framerate,
                    params.nframes,
                    params.comptype,
                    params.compname
                )
                left_channel.setparams(output_params)
                right_channel.setparams(output_params)
                for _i in range(params.nframes):
                    stereo_data = stereo_channel.readframes(1)
                    left_data = stereo_data[0:2]
                    right_data = stereo_data[2:4]
                    left_channel.writeframesraw(left_data)
                    right_channel.writeframesraw(right_data)

if __name__ == "__main__":
    try:
        if sys.argv[1] == "--to-stereo":
            mono_to_stereo(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == "--to-mono":
            stereo_to_mono(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            raise IndexError
    except IndexError:
        print("USAGE: %s --to-stereo left right stereo" % sys.argv[0])
        print("       %s --to-mono   stereo left right" % sys.argv[0])
        sys.exit(1)
