import wave
import struct
import math

filename = "output.wav"

wf = wave.open(filename, 'rb')
frames = wf.readframes(wf.getnframes())
wf.close()

count = len(frames) / 2
format_string = "%dh" % count

audio_data = struct.unpack(format_string, frames)

sum_squares = 0.0
for sample in audio_data:
    sum_squares += (sample * sample)

rms = math.sqrt(sum_squares / count)
print(f"RMS: {rms}")
if rms < 100:
    print("Audio signal is very weak or silent.")
else:
    print("Audio signal detected.")
