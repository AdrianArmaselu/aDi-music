from graphmodel import MidiUtils

__author__ = 'Adisor'


class MetaContext:
    def __init__(self, time_signature=None, tempo=None, key_signature=None, control=None, port=None, program=None):
        self.time_signature_event = time_signature
        self.tempo_event = tempo
        self.key_signature_event = key_signature
        self.control_event = control
        self.port_event = port
        self.program_event = program

    def copy(self):
        return MetaContext(self.time_signature_event, self.tempo_event, self.key_signature_event, self.control_event,
                           self.port_event, self.program_event)

    def update_from_event(self, event):
        if not MidiUtils.is_music_control_event(event):
            return
        if MidiUtils.is_time_signature_event(event):
            self.time_signature_event = event
        if MidiUtils.is_set_tempo_event(event):
            self.tempo_event = event
        if MidiUtils.is_key_signature_event(event):
            self.key_signature_event = event
        if MidiUtils.is_control_change_event(event):
            self.control_event = event
        if MidiUtils.is_port_event(event):
            self.port_event = event
        if MidiUtils.is_program_change_event(event):
            self.program_event = event

    def update_from_context(self, context):

        # global parameters
        if context.time_signature_event:
            self.time_signature_event = context.time_signature_event
        if context.key_signature_event:
            self.key_signature_event = context.key_signature_event
        if context.tempo_event:
            self.tempo_event = context.tempo_event

        # track parameters
        if context.control_event:
            self.control_event = context.control_event
        if context.port_event:
            self.port_event = context.port_event
        if context.program_event:
            self.program_event = context.program_event

    def __str__(self):
        string = str(self.time_signature_event) + ", " + str(self.tempo_event) + ", "
        string += str(self.key_signature_event) + ", " + str(self.control_event) + ", " + str(self.port_event) + ", "
        string += str(self.program_event)
        return string
