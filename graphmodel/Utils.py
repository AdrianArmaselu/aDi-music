from midi import TimeSignatureEvent, ProgramChangeEvent, SetTempoEvent, KeySignatureEvent, ControlChangeEvent, \
    PortEvent, \
    NoteOnEvent, NoteOffEvent
import midi

__author__ = 'Adisor'

music_control_events = [TimeSignatureEvent, SetTempoEvent, KeySignatureEvent, ControlChangeEvent, PortEvent,
                        ProgramChangeEvent]
"""
Consider: Polyphonic Aftertouch, Channel Aftertouch - how much a key is pressed more - for now we can ignore
Port Events can be ignored
Control Change and aftertouch - modulation and pitch bend
check MIT music21
"""


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
    event_type = get_event_type(event)
    return event_type != NoteOnEvent and event_type != NoteOffEvent


def is_music_control_event(event):
    """
    Checks to see if the event is an event that sets music control - meaning tempo, key signature etc.
    :param event: Midi Event
    :return: boolean
    """
    # TODO: test if this works
    event_type = get_event_type(event)
    return event_type in music_control_events


def is_time_signature_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return get_event_type(event) == TimeSignatureEvent


def is_set_tempo_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return get_event_type(event) == SetTempoEvent


def is_key_signature_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return get_event_type(event) == KeySignatureEvent


def is_control_change_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return get_event_type(event) == ControlChangeEvent


def is_port_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return get_event_type(event) == PortEvent


def is_program_change_event(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    return get_event_type(event) == ProgramChangeEvent


def has_note_ended(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    event_type = get_event_type(event)
    return event_type == NoteOffEvent or (event_type == NoteOnEvent and event.velocity == 0)


def is_new_note(event):
    """
    :param event: Midi Event
    :return: boolean
    """
    event_type = get_event_type(event)
    return event_type == NoteOnEvent and event.velocity > 0


def note_on_event(note):
    """
    :param note: Model Note
    :return: Midi Event
    """
    return midi.NoteOnEvent(channel=note.channel, tick=0, pitch=note.pitch,
                            velocity=note.velocity)


def note_off_event(note):
    """
    :param note: Model Note
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
    :param track:
    :param channel:
    :return:
    """
    for event in track:
        event.channel = channel
