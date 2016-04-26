from midi import events

__author__ = 'Adisor'

# classdict = {events.NoteOnEvent: "noteon", events.EndOfTrackEvent: "offnote", events.ControlChangeEvent: {}}
#
# classdict[events.ControlChangeEvent][23] = events.ControlChangeEvent(data=[23, 44])
# classdict[events.ControlChangeEvent][24] = events.ControlChangeEvent(data=[24, 44])
#
# classdict2 = {events.ControlChangeEvent: {}}
# classdict2[events.ControlChangeEvent][23] = events.ControlChangeEvent(data=[22, 44])
# classdict2[events.ControlChangeEvent][24] = events.ControlChangeEvent(data=[22, 44])
#
# print classdict2[events.ControlChangeEvent] == classdict[events.ControlChangeEvent]
#
# event = events.NoteOnEvent()
#
# print type(event)
# classdict[type(event)] = "noteon_changed"
# print classdict[events.EndOfTrackEvent]
# print classdict[events.NoteOnEvent]


data1 = [1, 2, 3, 4]
data2 = [1, 2, 2,4 ]

data2.append(data1)

print data2
print data1 != data2
