# encoding: utf-8

import decimal
import iomidi


class MIDIConverter(object):

    def __init__(self, event_mapper=None):
        self._event_mapper = self._get_event_mapper(event_mapper)

    def to_seq(self, midi_track):
        accumulated_time_ticks = 0
        event_mapper = self._event_mapper

        for event in midi_track.events:
            accumulated_time_ticks += event.delta
            event_descriptor = event_mapper(event)

            if event_descriptor is None:
                continue

            yield dict(
                type=event_descriptor['type'],
                channel=event_descriptor.get('channel', None),
                time_ticks=accumulated_time_ticks)

    def _get_event_mapper(self, user_mapper):
        if user_mapper is not None:
            return user_mapper

        def default_mapper(event):
            if not isinstance(event, iomidi.NoteOnEvent):
                return None
            return dict(type='beat')
        return default_mapper


def merge_time_sequences(seq_a, seq_b):
    rev_seq_a = list(reversed(seq_a))
    rev_seq_b = list(reversed(seq_b))

    while rev_seq_a and rev_seq_b:
        if rev_seq_a[-1]['time_ticks'] <= rev_seq_b[-1]['time_ticks']:
            yield rev_seq_a.pop()
        else:
            yield rev_seq_b.pop()

    while rev_seq_a:
        yield rev_seq_a.pop()
    while rev_seq_b:
        yield rev_seq_b.pop()

def sequences_with_ms(seq, midi_header):
    for event in seq:
        event['time_ms'] = ticks_to_ms(
            event['time_ticks'], midi_header.division)
        yield event

def ticks_to_ms(ticks, time_division):
    return float(
        # tick as milliseconds
        1 / decimal.Decimal(time_division) * 1000
        # multiplied by #ticks
        * ticks)
