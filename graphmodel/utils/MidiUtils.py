from midi import events
import midi

__author__ = 'Adisor'

"""
Class For utility Methods

ProgramChangeEvent: data - size 1, 1 byte

SetTempoEvent: data - size 3, 1 byte each

KeySignatureEvent: data - size 2, 1 byte each;
first byte number of sharps or flats
-7 = 7 flats
0 = key of C
+7 = 7 sharps
second byte
0 = major key
1 = minor key

TimeSignatureEvent: data - size 4, 1 byte each

Style Elements:
Tempo, Time Signature, Key Signature, Program Change(maybe), ControlChange(maybe)

Track Specific: PortEvent, ProgramChan geEvent, ControlChangeEvent - should be in each track (always)
Global: TempoEvent, KeySignatureEvent, TimeSignatureEvent - should be in first track (always)
"""
track_meta_events = [events.ControlChangeEvent, events.ProgramChangeEvent]
global_meta_events = [events.TimeSignatureEvent, events.SetTempoEvent, events.KeySignatureEvent]
music_control_events = track_meta_events + global_meta_events
processed_events = music_control_events + [events.NoteOnEvent, events.NoteOffEvent]
"""
Consider: Polyphonic Aftertouch, Channel Aftertouch - how much a key is pressed more - for now we can ignore
Port Events can be ignored
Control Change and aftertouch - modulation and pitch bend
check MIT music21
"""


def is_channel_event(event):
    """
    :param event: Midi event
    :return: boolean
    """
    return isinstance(event, events.Event)


def is_global_meta_event(event):
    """
    :param event: Midi event
    :return: boolean
    """
    return get_event_type(event) in global_meta_events


def is_track_meta_event(event):
    """
    :param event: Midi event
    :return: boolean
    """
    return get_event_type(event) in track_meta_events


def is_event_processed(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.MetaEventWithText) or get_event_type(event) in processed_events or \
           isinstance(event, events.EndOfTrackEvent)


def get_event_type(event):
    """
    :param event: Midi Event
    :return: the type of the Midi Event object
    """
    return type(event)


def is_meta_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.MetaEvent)


def is_music_control_event(event):
    """
    Checks to see if the event is an event that sets music control - meaning tempo, key signature etc.
    :param event: Midi Event
    :return: boolean
    """
    event_type = get_event_type(event)
    return event_type in music_control_events


def is_time_signature_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.TimeSignatureEvent)


def is_set_tempo_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.SetTempoEvent)


def is_event_with_channel(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.Event)


def is_key_signature_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.KeySignatureEvent)


def is_control_change_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.ControlChangeEvent)


def is_port_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.PortEvent)


def is_program_change_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.ProgramChangeEvent)


def has_note_ended(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.NoteOffEvent) or (isinstance(event, events.NoteOnEvent) and event.velocity == 0)


def is_new_note(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return isinstance(event, events.NoteOnEvent) and event.velocity > 0


def note_on_event(note):
    """
    :param note: model Note
    :return: Midi Event
    """
    return midi.NoteOnEvent(channel=note.channel, tick=0, pitch=note.pitch,
                            velocity=note.velocity)


def note_off_event(note):
    """
    :param note: model Note
    :return: Midi Event
    """
    return midi.NoteOnEvent(channel=note.channel, tick=0, pitch=note.pitch,
                            velocity=0)


def delete_tracks(pattern, start, stop):
    """
    Deletes tracks that are in the range
    :param pattern: midi pattern
    :param start: start index
    :param stop: end index
    :return: modified pattern
    """
    tracks = []
    for i in range(start, stop, 1):
        tracks.append(pattern[i])
    for track in tracks:
        pattern.remove(track)


def convert_channel(track, channel):
    """
    Converts all the notes in the track to the specified channel
    :param track: Midi Track
    :param channel: target conversion channel
    :return: Modified Midi Track
    """
    for event in track:
        event.channel = channel


def change_program(track, data):
    """
    Changes the data value of the ProgramChangeEvent event in the track
    :param track: Midi track
    :param data: array with 1 number element, specifying the the program change
    :return: track with modified ProgramChangeEvent
    """
    for event in track:
        if is_program_change_event(event):
            event.data = data


def change_key_signature(track, data):
    """
    Changes the data value of the key signature event in the track
    :param track: Midi track
    :param data: array with 2 bytes
    :return: track with modified key signature
    """
    for event in track:
        if is_key_signature_event(event):
            event.data = data


def get_channel(track):
    """
    Returns the channel of the track
    :param track: Midi track
    :return: channel number
    """
    for event in track:
        if is_event_with_channel(event):
            return event.channel
    return None


def get_program_change_event(track):
    """
    Returns the event that specifies the instrument of the track
    :param track:  Midi track
    :return: instrument event
    """
    return loop_track_and_return_event_on_condition(track, is_program_change_event)


def get_port_event(track):
    """
    Returns the port event of the track
    :param track:
    :return: port event
    """
    return loop_track_and_return_event_on_condition(track, is_port_event)


def get_time_signature_event(pattern):
    """
    Returns the time signature of the entire musical piece
    :param pattern: Midi pattern
    :return: time signature event
    """
    return loop_track_and_return_event_on_condition(pattern[0], is_time_signature_event)


def get_key_signature_event(pattern):
    """
    Returns the key signature event of the entire musical piece
    :param pattern: Midi pattern
    :return: key signature event
    """
    return loop_track_and_return_event_on_condition(pattern[0], is_key_signature_event)


def loop_track_and_return_event_on_condition(track, condition):
    """
    :param track: Midi track
    :param condition: boolean function
    :return: Midi event
    """
    for event in track:
        if condition(event):
            return event
    return None
