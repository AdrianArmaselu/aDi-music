import os

def midi_to_mp3(midifile):
  command = "timidity -Ow -o - " + midifile + " | lame - output.mp3"
  os.system(command)

midi_to_mp3("bach.mid")