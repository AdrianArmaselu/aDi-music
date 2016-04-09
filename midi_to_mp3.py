import os

def midi_to_mp3(midifile, outputfile):
  command = "timidity -Ow -o - " + midifile + " | lame - output/" + outputfile
  os.system(command)

midi_to_mp3("k.mid", "output.mp3")