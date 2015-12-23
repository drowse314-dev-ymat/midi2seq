# encoding: utf-8

import sys
import random
import decimal
import json
import argparse
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
    rev_seq_a = list(reversed(list(seq_a)))
    rev_seq_b = list(reversed(list(seq_b)))

    while rev_seq_a and rev_seq_b:
        if rev_seq_a[-1]['time_ticks'] <= rev_seq_b[-1]['time_ticks']:
            yield rev_seq_a.pop()
        else:
            yield rev_seq_b.pop()

    while rev_seq_a:
        yield rev_seq_a.pop()
    while rev_seq_b:
        yield rev_seq_b.pop()

def sequence_with_ms(seq, midi_header):
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


def CLI(args):
    song = iomidi.read(args.midifile)
    converter = MIDIConverter()

    sequences = (
        sequence_with_ms(
            converter.to_seq(track),
            song.header)
        for track in song.tracks)

    merged_sequence = reduce(
        merge_time_sequences,
        sequences,
        [])

    channelled_sequence = random_channeler(
        merged_sequence,
        list(range(1, 10)))

    sys.stdout.write(
        json.dumps(list(channelled_sequence)))

def random_channeler(seq, channels=[0, 1]):
    channel = random.choice(channels)
    suc = dict(time_ticks=-1, channel=channel)
    for event in seq:
        while (
            suc['time_ticks'] != event['time_ticks'] and
            channel == suc['channel']):

            channel = random.choice(channels)

        event['channel'] = channel
        suc = event
        yield event


if __name__ == '__main__':
    argX = argparse.ArgumentParser()

    argX.add_argument('midifile')

    args = argX.parse_args()
    CLI(args)
