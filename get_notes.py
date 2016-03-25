import mido
import operator


class Note(object):
    def __init__(self, duration, start_time, pitch, channel, velocity):
        self.duration = duration
        self.start_time = start_time
        self.pitch = pitch
        self.channel = channel
        self.velocity = velocity

def getNotes(midi_file):
    mgs = []
    time_elasped = 0
    f = mido.MidiFile(midi_file)
    for m in f.play():
        time_elasped += m.time
        mgs.append([m,time_elasped])

    events = {}
    notes = {}

    for (message, time) in mgs:
        if message.type != 'note_on' and message.type != 'note_off':
            continue
        if message.type == 'note_off' or message.velocity == 0:
            (message0, start_time) = events[message.channel][message.note]
            del events[message.channel][message.note]
            duration = time - start_time
            new_note = Note(duration, start_time, message.note, message.channel, message0.velocity)
            if new_note.start_time not in notes:
                notes[new_note.start_time] = {}
            if new_note.channel not in notes[new_note.start_time]:
                notes[new_note.start_time][new_note.channel] = []
            notes[new_note.start_time][new_note.channel].append(new_note)
        else:
            if message.channel not in events:
                events[message.channel] = {}
            events[message.channel][message.note] = (message, time)

    notes = sorted(notes.items(), key=operator.itemgetter(0)) #sort according to key, which is the start_time of a note
    formatted_notes = []
    for (start_time, note_list) in notes:
        formatted_notes.append(sorted(note_list.items(), key=operator.itemgetter(0))[0][1])
    return formatted_notes

getNotes("bach.mid")
